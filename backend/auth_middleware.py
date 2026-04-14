"""
Authentication middleware.
Verify JWT tokens and extract user information.
"""

from typing import Optional, Tuple
from functools import wraps
from flask import request
from auth_service import get_auth_service


def get_auth_token(request_obj) -> Optional[str]:
    """
    Extract JWT token from Authorization header.
    Expected format: Authorization: Bearer <token>
    """
    auth_header = request_obj.headers.get('Authorization', '')
    if not auth_header.startswith('Bearer '):
        return None
    return auth_header[7:]  # Skip "Bearer "


def verify_token(token: str) -> Tuple[Optional[int], Optional[str]]:
    """
    Verify JWT token and extract user_id.
    
    Returns:
        (user_id, error_message)
    """
    auth_service = get_auth_service()
    payload = auth_service.verify_token(token)
    
    if not payload:
        return None, "Invalid or expired token"
    
    user_id = payload.get("user_id")
    if not user_id:
        return None, "Invalid token: no user_id"
    
    return user_id, None


def require_auth(f):
    """
    Decorator: require valid JWT authentication.
    Injects user_id into route function.
    
    Usage:
        @app.route('/api/protected')
        @require_auth
        def protected_route(user_id):
            ...
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = get_auth_token(request)
        if not token:
            return {"success": False, "error": "Missing authorization token"}, 401
        
        user_id, error = verify_token(token)
        if error:
            return {"success": False, "error": error}, 401
        
        return f(user_id=user_id, *args, **kwargs)
    
    return decorated_function
