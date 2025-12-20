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
from utils.storage import save_uploaded_file, get_absolute_path
from database.db import execute_query
from config import Config

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
        
        # Save Grad-CAM images
        gradcam_paths = save_gradcam_images(
            Config.GRADCAM_FOLDER,
            file_id,
            original,
            heatmap_colored,
            overlay
        )
        
        # Store prediction in database
        insert_query = """
            INSERT INTO images 
            (doctor_id, patient_id, original_image_uri, gradcam_image_uri, 
             predicted_label, prob_tumor, prob_no_tumor)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """
        prediction_id = execute_query(
            insert_query,
            (
                doctor_id,
                patient_id,
                file_path,
                gradcam_paths['overlay'],
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
    Get prediction history for current user
    
    Response JSON:
        {
            "success": true,
            "predictions": [
                {
                    "id": 123,
                    "predicted_label": "tumor",
                    "confidence": 0.9523,
                    "uploaded_at": "2025-12-19T10:30:00"
                },
                ...
            ]
        }
    """
    try:
        # Check authentication
        if 'user_id' not in session:
            return jsonify({'success': False, 'message': 'Authentication required'}), 401
        
        user_id = session['user_id']
        user_role = session['user_role']
        
        # Query based on role
        if user_role == 'doctor' or user_role == 'admin':
            # Doctors see all predictions they uploaded
            query = """
                SELECT id, predicted_label, prob_tumor, prob_no_tumor, 
                       uploaded_at, patient_id
                FROM images 
                WHERE doctor_id = %s 
                ORDER BY uploaded_at DESC
            """
            predictions = execute_query(query, (user_id,))
        else:
            # Patients see only their own predictions
            query = """
                SELECT id, predicted_label, prob_tumor, prob_no_tumor, 
                       uploaded_at, doctor_id
                FROM images 
                WHERE patient_id = %s 
                ORDER BY uploaded_at DESC
            """
            predictions = execute_query(query, (user_id,))
        
        # Add confidence field
        for pred in predictions:
            if pred['predicted_label'] == 'tumor':
                pred['confidence'] = float(pred['prob_tumor'])
            else:
                pred['confidence'] = float(pred['prob_no_tumor'])
        
        return jsonify({
            'success': True,
            'predictions': predictions
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error retrieving history: {str(e)}'
        }), 500
