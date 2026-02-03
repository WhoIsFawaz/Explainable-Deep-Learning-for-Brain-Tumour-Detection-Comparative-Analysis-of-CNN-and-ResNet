"""
Prediction endpoint for brain MRI classification
"""
from flask import Blueprint, request, jsonify, session
from werkzeug.utils import secure_filename
import torch
from datetime import datetime

from models.resnet50_model import get_model
from models.gradcam import GradCAM, create_gradcam_overlay, save_gradcam_images
from utils.preprocessing import preprocess_image, validate_image_file
from utils.storage import save_uploaded_file, get_absolute_path, USE_AZURE_STORAGE
from database.db import execute_query
from config import Config
import os

predict_bp = Blueprint('predict', __name__, url_prefix='/api')

@predict_bp.route('/predict', methods=['POST'])
def predict():
    """
    Brain MRI prediction endpoint with Grad-CAM visualization
    
    Request:
        - Multipart form data with 'image' file
        - Optional: 'patient_id' in form data
    
    Response JSON:
        {
            "success": true,
            "prediction": {
                "id": 123,
                "predicted_label": "tumor",
                "probabilities": {
                    "tumor": 0.9523,
                    "no_tumor": 0.0477
                },
                "confidence": 0.9523,
                "gradcam_urls": {
                    "original": "gradcam_outputs/uuid_original.png",
                    "heatmap": "gradcam_outputs/uuid_heatmap.png",
                    "overlay": "gradcam_outputs/uuid_overlay.png"
                },
                "uploaded_at": "2025-12-19T10:30:00"
            }
        }
    """
    try:
        # Check authentication
        if 'user_id' not in session:
            return jsonify({'success': False, 'message': 'Authentication required'}), 401
        
        doctor_id = session['user_id']
        
        # Check if image file is present
        if 'image' not in request.files:
            return jsonify({'success': False, 'message': 'No image file provided'}), 400
        
        file = request.files['image']
        
        # Validate image file
        try:
            validate_image_file(file)
        except ValueError as e:
            return jsonify({'success': False, 'message': str(e)}), 400
        
        # Get patient_id from form data (optional for now, default to doctor)
        patient_id = request.form.get('patient_id', doctor_id)
        
        # Save uploaded file
        file_path, file_id = save_uploaded_file(file)
        abs_file_path = get_absolute_path(file_path)
        
        # Track if we need to clean up temp file
        is_temp_file = USE_AZURE_STORAGE and abs_file_path.startswith('/tmp')
        
        try:
            # Preprocess image
            image_tensor, _ = preprocess_image(abs_file_path)
            
            # Load model (singleton, loads once)
            model = get_model()
            
            # Run prediction
            predicted_class, probabilities = model.predict(image_tensor)
            predicted_label = 'tumor' if predicted_class == 1 else 'no_tumor'
            confidence = probabilities[predicted_label]
            
            # Generate Grad-CAM
            target_layer = model.get_target_layer()
            gradcam = GradCAM(model.model, target_layer)
            
            image_tensor_gradcam = image_tensor.to(model.device)
            heatmap, _ = gradcam.generate_heatmap(image_tensor_gradcam, class_idx=predicted_class)
            
            # Create Grad-CAM overlay
            original, heatmap_colored, overlay = create_gradcam_overlay(
                abs_file_path, 
                heatmap, 
                img_size=Config.IMG_SIZE
            )
        finally:
            # Clean up temp file if it was downloaded from Azure
            if is_temp_file and os.path.exists(abs_file_path):
                os.remove(abs_file_path)
        
        # Save Grad-CAM images
        gradcam_paths = save_gradcam_images(
            Config.GRADCAM_FOLDER,
            file_id,
            original,
            heatmap_colored,
            overlay
        )
        
        # Store prediction in database
        # Store all 3 processed images from gradcam_outputs (consistent sizing)
        insert_query = """
            INSERT INTO images 
            (doctor_id, patient_id, original_image_uri, heatmap_image_uri, overlay_image_uri,
             predicted_label, prob_tumor, prob_no_tumor)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """
        prediction_id = execute_query(
            insert_query,
            (
                doctor_id,
                patient_id,
                gradcam_paths['original'],   # Use processed original from gradcam_outputs
                gradcam_paths['heatmap'],    # Heatmap from gradcam_outputs
                gradcam_paths['overlay'],    # Overlay from gradcam_outputs
                predicted_label,
                probabilities['tumor'],
                probabilities['no_tumor']
            ),
            commit=True
        )
        
        # Return response
        return jsonify({
            'success': True,
            'prediction': {
                'id': prediction_id,
                'predicted_label': predicted_label,
                'probabilities': probabilities,
                'confidence': confidence,
                'gradcam_urls': {
                    'original': gradcam_paths['original'],
                    'heatmap': gradcam_paths['heatmap'],
                    'overlay': gradcam_paths['overlay']
                },
                'uploaded_at': datetime.now().isoformat()
            }
        }), 200
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False, 
            'message': f'Prediction error: {str(e)}'
        }), 500

@predict_bp.route('/predictions/<int:prediction_id>', methods=['GET'])
def get_prediction(prediction_id):
    """
    Retrieve a specific prediction by ID
    
    Response JSON:
        {
            "success": true,
            "prediction": {
                "id": 123,
                "predicted_label": "tumor",
                "prob_tumor": 0.9523,
                "prob_no_tumor": 0.0477,
                "original_image_uri": "uploads/uuid.png",
                "gradcam_image_uri": "gradcam_outputs/uuid_overlay.png",
                "uploaded_at": "2025-12-19T10:30:00"
            }
        }
    """
    try:
        # Check authentication
        if 'user_id' not in session:
            return jsonify({'success': False, 'message': 'Authentication required'}), 401
        
        # Query prediction
        query = "SELECT * FROM images WHERE id = %s"
        prediction = execute_query(query, (prediction_id,), fetch_one=True)
        
        if not prediction:
            return jsonify({'success': False, 'message': 'Prediction not found'}), 404
        
        return jsonify({
            'success': True,
            'prediction': prediction
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error retrieving prediction: {str(e)}'
        }), 500

@predict_bp.route('/predictions/history', methods=['GET'])
def get_predictions_history():
    """
    Get prediction history
    - Doctors: Can filter by patient_id or see all their predictions
    - Patients: See only their own predictions filtered by doctor_id
    
    Query params:
        - patient_id (for doctors)
        - doctor_id (for patients)
    """
    try:
        if 'user_id' not in session:
            return jsonify({'success': False, 'message': 'Authentication required'}), 401
        
        user_id = session['user_id']
        user_role = session['user_role']
        patient_id = request.args.get('patient_id', type=int)
        doctor_id = request.args.get('doctor_id', type=int)
        
        if user_role == 'doctor':
            # Doctor viewing specific patient or all patients
            if patient_id:
                query = """
                    SELECT i.*, p.name as patient_name 
                    FROM images i 
                    JOIN users p ON i.patient_id = p.id 
                    WHERE i.doctor_id = %s AND i.patient_id = %s 
                    ORDER BY i.uploaded_at DESC
                """
                predictions = execute_query(query, (user_id, patient_id))
            else:
                query = """
                    SELECT i.*, p.name as patient_name 
                    FROM images i 
                    JOIN users p ON i.patient_id = p.id 
                    WHERE i.doctor_id = %s 
                    ORDER BY i.uploaded_at DESC
                """
                predictions = execute_query(query, (user_id,))
        
        elif user_role == 'patient':
            # Patient viewing specific doctor or all doctors
            if doctor_id:
                query = """
                    SELECT i.*, d.name as doctor_name 
                    FROM images i 
                    JOIN users d ON i.doctor_id = d.id 
                    WHERE i.patient_id = %s AND i.doctor_id = %s 
                    ORDER BY i.uploaded_at DESC
                """
                predictions = execute_query(query, (user_id, doctor_id))
            else:
                query = """
                    SELECT i.*, d.name as doctor_name 
                    FROM images i 
                    JOIN users d ON i.doctor_id = d.id 
                    WHERE i.patient_id = %s 
                    ORDER BY i.uploaded_at DESC
                """
                predictions = execute_query(query, (user_id,))
        
        else:
            return jsonify({'success': False, 'message': 'Invalid role'}), 403
        
        # Add confidence field
        for pred in predictions:
            if pred['predicted_label'] == 'tumor':
                pred['confidence'] = float(pred['prob_tumor'])
            else:
                pred['confidence'] = float(pred['prob_no_tumor'])
        
        return jsonify({'success': True, 'predictions': predictions}), 200
        
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@predict_bp.route('/patients', methods=['GET'])
def get_patients():
    """Get list of patients for doctor's dropdown"""
    try:
        if 'user_id' not in session or session['user_role'] != 'doctor':
            return jsonify({'success': False, 'message': 'Doctor access required'}), 403
        
        query = "SELECT id, name, email FROM users WHERE role = 'patient' ORDER BY name"
        patients = execute_query(query)
        
        return jsonify({'success': True, 'patients': patients}), 200
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@predict_bp.route('/doctors', methods=['GET'])
def get_doctors():
    """Get list of doctors for patient's dropdown"""
    try:
        if 'user_id' not in session or session['user_role'] != 'patient':
            return jsonify({'success': False, 'message': 'Patient access required'}), 403
        
        # Get doctors who have treated this patient
        patient_id = session['user_id']
        query = """
            SELECT DISTINCT u.id, u.name, u.email 
            FROM users u 
            JOIN images i ON u.id = i.doctor_id 
            WHERE i.patient_id = %s AND u.role = 'doctor'
            ORDER BY u.name
        """
        doctors = execute_query(query, (patient_id,))
        
        return jsonify({'success': True, 'doctors': doctors}), 200
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

