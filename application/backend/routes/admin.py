"""
Admin routes for user management
"""
from flask import Blueprint, request, jsonify, session
import bcrypt
from database.db import execute_query

admin_bp = Blueprint('admin', __name__, url_prefix='/api/admin')

def admin_required(f):
    """Decorator to check if user is admin"""
    def wrapper(*args, **kwargs):
        if 'user_role' not in session or session['user_role'] != 'admin':
            return jsonify({'success': False, 'message': 'Admin access required'}), 403
        return f(*args, **kwargs)
    wrapper.__name__ = f.__name__
    return wrapper

@admin_bp.route('/users', methods=['GET'])
@admin_required
def get_all_users():
    """Get all users (doctors and patients)"""
    try:
        query = "SELECT id, name, email, role, created_at FROM users ORDER BY created_at DESC"
        users = execute_query(query)
        return jsonify({'success': True, 'users': users}), 200
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@admin_bp.route('/create-doctor', methods=['POST'])
@admin_required
def create_doctor():
    """Create new doctor account"""
    try:
        data = request.get_json()
        name = data.get('name')
        email = data.get('email')
        password = data.get('password')
        
        if not all([name, email, password]):
            return jsonify({'success': False, 'message': 'All fields required'}), 400
        
        # Check if email exists
        check_query = "SELECT id FROM users WHERE email = %s"
        existing = execute_query(check_query, (email,), fetch_one=True)
        if existing:
            return jsonify({'success': False, 'message': 'Email already exists'}), 400
        
        # Hash password
        password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        
        # Insert doctor
        insert_query = "INSERT INTO users (name, email, password_hash, role) VALUES (%s, %s, %s, 'doctor')"
        user_id = execute_query(insert_query, (name, email, password_hash), commit=True)
        
        return jsonify({
            'success': True,
            'message': 'Doctor created successfully',
            'user': {'id': user_id, 'name': name, 'email': email, 'role': 'doctor'}
        }), 201
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@admin_bp.route('/create-patient', methods=['POST'])
@admin_required
def create_patient():
    """Create new patient account"""
    try:
        data = request.get_json()
        name = data.get('name')
        email = data.get('email')
        password = data.get('password')
        
        if not all([name, email, password]):
            return jsonify({'success': False, 'message': 'All fields required'}), 400
        
        # Check if email exists
        check_query = "SELECT id FROM users WHERE email = %s"
        existing = execute_query(check_query, (email,), fetch_one=True)
        if existing:
            return jsonify({'success': False, 'message': 'Email already exists'}), 400
        
        # Hash password
        password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        
        # Insert patient
        insert_query = "INSERT INTO users (name, email, password_hash, role) VALUES (%s, %s, %s, 'patient')"
        user_id = execute_query(insert_query, (name, email, password_hash), commit=True)
        
        return jsonify({
            'success': True,
            'message': 'Patient created successfully',
            'user': {'id': user_id, 'name': name, 'email': email, 'role': 'patient'}
        }), 201
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@admin_bp.route('/delete-user/<int:user_id>', methods=['DELETE'])
@admin_required
def delete_user(user_id):
    """Delete user account"""
    try:
        # Prevent self-deletion
        if user_id == session['user_id']:
            return jsonify({'success': False, 'message': 'Cannot delete own account'}), 400
        
        query = "DELETE FROM users WHERE id = %s"
        execute_query(query, (user_id,), commit=True)
        
        return jsonify({'success': True, 'message': 'User deleted successfully'}), 200
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500
