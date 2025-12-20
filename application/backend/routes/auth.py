"""
Authentication routes (login, logout, user management)
"""
from flask import Blueprint, request, jsonify, session
import bcrypt
from database.db import execute_query

auth_bp = Blueprint('auth', __name__, url_prefix='/api/auth')

@auth_bp.route('/login', methods=['POST'])
def login():
    """
    User login endpoint
    
    Request JSON:
        {
            "email": "doctor@test.com",
            "password": "admin123"
        }
    
    Response JSON:
        {
            "success": true,
            "message": "Login successful",
            "user": {
                "id": 2,
                "name": "Dr. Sarah Johnson",
                "email": "doctor@test.com",
                "role": "doctor"
            }
        }
    """
    try:
        data = request.get_json()
        email = data.get('email')
        password = data.get('password')
        
        if not email or not password:
            return jsonify({'success': False, 'message': 'Email and password required'}), 400
        
        # Query user from database
        query = "SELECT * FROM users WHERE email = %s"
        user = execute_query(query, (email,), fetch_one=True)
        
        if not user:
            return jsonify({'success': False, 'message': 'Invalid credentials'}), 401
        
        # Verify password
        password_bytes = password.encode('utf-8')
        hash_bytes = user['password_hash'].encode('utf-8')
        
        if not bcrypt.checkpw(password_bytes, hash_bytes):
            return jsonify({'success': False, 'message': 'Invalid credentials'}), 401
        
        # Store user in session
        session['user_id'] = user['id']
        session['user_email'] = user['email']
        session['user_role'] = user['role']
        
        return jsonify({
            'success': True,
            'message': 'Login successful',
            'user': {
                'id': user['id'],
                'name': user['name'],
                'email': user['email'],
                'role': user['role']
            }
        }), 200
        
    except Exception as e:
        return jsonify({'success': False, 'message': f'Login error: {str(e)}'}), 500

@auth_bp.route('/logout', methods=['POST'])
def logout():
    """
    User logout endpoint
    
    Response JSON:
        {
            "success": true,
            "message": "Logout successful"
        }
    """
    try:
        session.clear()
        return jsonify({'success': True, 'message': 'Logout successful'}), 200
    except Exception as e:
        return jsonify({'success': False, 'message': f'Logout error: {str(e)}'}), 500

@auth_bp.route('/me', methods=['GET'])
def get_current_user():
    """
    Get current logged-in user info
    
    Response JSON:
        {
            "success": true,
            "user": {
                "id": 2,
                "email": "doctor@test.com",
                "role": "doctor"
            }
        }
    """
    try:
        if 'user_id' not in session:
            return jsonify({'success': False, 'message': 'Not authenticated'}), 401
        
        return jsonify({
            'success': True,
            'user': {
                'id': session['user_id'],
                'email': session['user_email'],
                'role': session['user_role']
            }
        }), 200
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error: {str(e)}'}), 500

@auth_bp.route('/register', methods=['POST'])
def register_user():
    """
    Admin endpoint to create new users
    
    Request JSON:
        {
            "name": "Dr. John Doe",
            "email": "john@test.com",
            "password": "password123",
            "role": "doctor"
        }
    
    Response JSON:
        {
            "success": true,
            "message": "User created successfully",
            "user_id": 4
        }
    """
    try:
        # Check if admin
        if 'user_role' not in session or session['user_role'] != 'admin':
            return jsonify({'success': False, 'message': 'Admin access required'}), 403
        
        data = request.get_json()
        name = data.get('name')
        email = data.get('email')
        password = data.get('password')
        role = data.get('role', 'patient')
        
        if not name or not email or not password:
            return jsonify({'success': False, 'message': 'Name, email, and password required'}), 400
        
        # Check if email already exists
        check_query = "SELECT id FROM users WHERE email = %s"
        existing = execute_query(check_query, (email,), fetch_one=True)
        if existing:
            return jsonify({'success': False, 'message': 'Email already registered'}), 400
        
        # Hash password
        password_bytes = password.encode('utf-8')
        salt = bcrypt.gensalt()
        password_hash = bcrypt.hashpw(password_bytes, salt).decode('utf-8')
        
        # Insert user
        insert_query = """
            INSERT INTO users (name, email, password_hash, role)
            VALUES (%s, %s, %s, %s)
        """
        user_id = execute_query(insert_query, (name, email, password_hash, role), commit=True)
        
        return jsonify({
            'success': True,
            'message': 'User created successfully',
            'user_id': user_id
        }), 201
        
    except Exception as e:
        return jsonify({'success': False, 'message': f'Registration error: {str(e)}'}), 500
