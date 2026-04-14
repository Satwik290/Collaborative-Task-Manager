"""
Authentication routes.
POST /api/auth/register
POST /api/auth/login
POST /api/auth/logout
"""

from flask import Blueprint, request, jsonify
from database import get_db
from auth_service import get_auth_service
from schemas import RegisterRequest, LoginRequest, success_response, error_response, user_to_dict

auth_bp = Blueprint('auth', __name__, url_prefix='/api/auth')


@auth_bp.route('/register', methods=['POST'])
def register():
    """
    Register a new user.
    
    Request:
        {
            "email": "user@example.com",
            "password": "password123"
        }
    
    Response:
        {
            "success": true,
            "data": {
                "id": 1,
                "email": "user@example.com",
                "created_at": "2024-01-01T00:00:00"
            }
        }
    """
    # Parse request
    data = request.get_json(silent=True) or {}
    req, error = RegisterRequest.from_json(data)
    if error:
        return jsonify(error_response(error)), 400
    
    # Register user
    db = get_db()
    auth_service = get_auth_service()
    
    user, error = auth_service.register_user(db, req.email, req.password)
    db.close()
    
    if error:
        return jsonify(error_response(error)), 400
    
    return jsonify(success_response(user_to_dict(user))), 201


@auth_bp.route('/login', methods=['POST'])
def login():
    """
    Authenticate user and return JWT token.
    
    Request:
        {
            "email": "user@example.com",
            "password": "password123"
        }
    
    Response:
        {
            "success": true,
            "data": {
                "token": "eyJ0eXAiOiJKV1QiLCJhbGc..."
            }
        }
    """
    # Parse request
    data = request.get_json(silent=True) or {}
    req, error = LoginRequest.from_json(data)
    if error:
        return jsonify(error_response(error)), 400
    
    # Authenticate
    db = get_db()
    auth_service = get_auth_service()
    
    token, error = auth_service.login_user(db, req.email, req.password)
    db.close()
    
    if error:
        return jsonify(error_response(error)), 401
    
    return jsonify(success_response({"token": token})), 200


@auth_bp.route('/logout', methods=['POST'])
def logout():
    """
    Logout user (stateless - just return success).
    Client should discard token.
    """
    return jsonify(success_response()), 200
