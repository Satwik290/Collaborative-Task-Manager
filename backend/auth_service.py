"""
Authentication service.
Handles user registration, login, JWT generation.
"""

import jwt
import os
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy.orm import Session
from models import User


class AuthService:
    """
    Pure business logic for authentication.
    No Flask dependencies - testable in isolation.
    """
    
    def __init__(self, secret_key: str = None, token_expiry_hours: int = 24):
        """
        Initialize auth service.
        
        Args:
            secret_key: JWT signing key (defaults to env var JWT_SECRET_KEY)
            token_expiry_hours: How long tokens are valid
        """
        self.secret_key = secret_key or os.getenv("JWT_SECRET_KEY", "dev-secret-key")
        self.token_expiry_hours = token_expiry_hours
    
    def hash_password(self, password: str) -> str:
        """
        Hash a plaintext password securely.
        Returns hashed password safe for storage.
        """
        if not password or len(password) < 6:
            raise ValueError("Password must be at least 6 characters")
        return generate_password_hash(password)
    
    def verify_password(self, password: str, hash: str) -> bool:
        """
        Check if plaintext password matches hash.
        """
        return check_password_hash(hash, password)
    
    def create_token(self, user_id: int, email: str) -> str:
        """
        Generate JWT token for user.
        
        Args:
            user_id: User's database ID
            email: User's email (for debugging/logs)
        
        Returns:
            JWT token string
        
        Raises:
            ValueError: If inputs invalid
        """
        if not user_id or not email:
            raise ValueError("user_id and email required")
        
        payload = {
            "user_id": user_id,
            "email": email,
            "iat": datetime.utcnow(),
            "exp": datetime.utcnow() + timedelta(hours=self.token_expiry_hours)
        }
        
        token = jwt.encode(payload, self.secret_key, algorithm="HS256")
        return token
    
    def verify_token(self, token: str) -> Optional[Dict[str, Any]]:
        """
        Decode and verify JWT token.
        
        Args:
            token: JWT token string
        
        Returns:
            Decoded payload dict if valid, None if invalid/expired
        """
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=["HS256"])
            return payload
        except jwt.ExpiredSignatureError:
            return None
        except jwt.InvalidTokenError:
            return None
    
    def register_user(self, db: Session, email: str, password: str) -> tuple[User, Optional[str]]:
        """
        Register a new user.
        
        Args:
            db: Database session
            email: User email
            password: Plaintext password
        
        Returns:
            (User object, error_message)
            If successful: (User, None)
            If failed: (None, "error message")
        """
        # Validate inputs
        if not email or "@" not in email:
            return None, "Invalid email address"
        
        if not password or len(password) < 6:
            return None, "Password must be at least 6 characters"
        
        # Check if user exists
        existing = db.query(User).filter(User.email == email).first()
        if existing:
            return None, "Email already registered"
        
        # Create user
        try:
            password_hash = self.hash_password(password)
            user = User(email=email, password_hash=password_hash)
            db.add(user)
            db.commit()
            db.refresh(user)
            return user, None
        except Exception as e:
            db.rollback()
            return None, f"Registration failed: {str(e)}"
    
    def login_user(self, db: Session, email: str, password: str) -> tuple[Optional[str], Optional[str]]:
        """
        Authenticate user and return token.
        
        Args:
            db: Database session
            email: User email
            password: Plaintext password
        
        Returns:
            (token, error_message)
            If successful: (token_string, None)
            If failed: (None, "error message")
        """
        if not email or not password:
            return None, "Email and password required"
        
        # Find user by email
        user = db.query(User).filter(User.email == email).first()
        if not user:
            return None, "Invalid email or password"
        
        # Verify password
        if not self.verify_password(password, user.password_hash):
            return None, "Invalid email or password"
        
        # Generate token
        try:
            token = self.create_token(user.id, user.email)
            return token, None
        except Exception as e:
            return None, f"Login failed: {str(e)}"


# Global instance
_auth_service = None


def get_auth_service() -> AuthService:
    """Get global auth service instance"""
    global _auth_service
    if _auth_service is None:
        _auth_service = AuthService()
    return _auth_service
