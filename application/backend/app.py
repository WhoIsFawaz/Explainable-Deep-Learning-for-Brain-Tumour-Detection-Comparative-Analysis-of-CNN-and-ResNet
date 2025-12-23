"""
Brain MRI Classification System - Flask Backend
Main application entry point
"""
from flask import Flask, jsonify, send_from_directory
from flask_cors import CORS
from flask_session import Session
import os

from config import Config
from routes.auth import auth_bp
from routes.predict import predict_bp
from routes.admin import admin_bp

# Initialize Flask app
app = Flask(__name__)
app.config.from_object(Config)

# Configure CORS (allow frontend to communicate)
CORS(app, 
     supports_credentials=True, 
     resources={r"/api/*": {"origins": "http://localhost:3000"}},
     allow_headers=["Content-Type", "Authorization"],
     methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"])

# Configure server-side sessions
Session(app)

# Create upload directories if they don't exist
os.makedirs(Config.UPLOAD_FOLDER, exist_ok=True)
os.makedirs(Config.GRADCAM_FOLDER, exist_ok=True)

# Register blueprints
app.register_blueprint(auth_bp)
app.register_blueprint(admin_bp)
app.register_blueprint(predict_bp)

# Serve static files (Grad-CAM outputs and uploaded images)
@app.route('/gradcam_outputs/<path:filename>')
def serve_gradcam(filename):
    """Serve Grad-CAM output images"""
    return send_from_directory(Config.GRADCAM_FOLDER, filename)

@app.route('/uploads/<path:filename>')
def serve_uploads(filename):
    """Serve uploaded MRI images"""
    return send_from_directory(Config.UPLOAD_FOLDER, filename)

# Health check endpoint
@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'service': 'Brain MRI Classification API',
        'version': '1.0.0'
    }), 200

# Root endpoint
@app.route('/', methods=['GET'])
def root():
    """Root endpoint with API documentation"""
    return jsonify({
        'message': 'Brain MRI Classification API',
        'version': '1.0.0',
        'endpoints': {
            'health': '/health',
            'auth': {
                'login': 'POST /api/auth/login',
                'logout': 'POST /api/auth/logout',
                'me': 'GET /api/auth/me',
                'register': 'POST /api/auth/register (admin only)'
            },
            'prediction': {
                'predict': 'POST /api/predict',
                'get_prediction': 'GET /api/predictions/<id>',
                'history': 'GET /api/predictions/history'
            }
        }
    }), 200

# Error handlers
@app.errorhandler(404)
def not_found(error):
    return jsonify({'success': False, 'message': 'Endpoint not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'success': False, 'message': 'Internal server error'}), 500

if __name__ == '__main__':
    print("=" * 70)
    print("Brain MRI Classification System - Backend Server")
    print("=" * 70)
    print(f"Environment: {Config.DEBUG and 'Development' or 'Production'}")
    print(f"Database: {Config.DB_HOST}:{Config.DB_PORT}/{Config.DB_NAME}")
    print(f"Model: {Config.MODEL_PATH}")
    print(f"Server: http://localhost:5000")
    print("=" * 70)
    print("\nStarting Flask server...\n")
    
    app.run(
        host='0.0.0.0',
        port=5000,
        debug=Config.DEBUG
    )
