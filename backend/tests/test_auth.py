"""
Tests for authentication service and routes.
"""

import pytest
from auth_service import AuthService
from models import User
import json


class TestAuthService:
    """Test business logic"""
    
    def test_hash_password(self):
        """Passwords are hashed, not stored plaintext"""
        service = AuthService()
        hash1 = service.hash_password("mypassword")
        hash2 = service.hash_password("mypassword")
        
        # Same password produces different hashes (salt)
        assert hash1 != hash2
        # Both verify correctly
        assert service.verify_password("mypassword", hash1)
        assert service.verify_password("mypassword", hash2)
        # Wrong password fails
        assert not service.verify_password("wrongpassword", hash1)
    
    def test_hash_password_rejects_short_password(self):
        """Short passwords rejected"""
        service = AuthService()
        with pytest.raises(ValueError):
            service.hash_password("short")
    
    def test_create_token(self):
        """Token creation and verification"""
        service = AuthService()
        token = service.create_token(123, "user@example.com")
        
        assert token is not None
        
        # Token verifies
        payload = service.verify_token(token)
        assert payload is not None
        assert payload["user_id"] == 123
        assert payload["email"] == "user@example.com"
    
    def test_verify_invalid_token(self):
        """Invalid tokens fail verification"""
        service = AuthService()
        
        assert service.verify_token("invalid") is None
        assert service.verify_token("") is None
    
    def test_register_user(self, test_db):
        """User registration"""
        service = AuthService()
        
        user, error = service.register_user(test_db, "new@example.com", "password123")
        
        assert error is None
        assert user is not None
        assert user.email == "new@example.com"
        assert user.id is not None
    
    def test_register_user_duplicate_email(self, test_db):
        """Cannot register same email twice"""
        service = AuthService()
        
        # First registration succeeds
        user1, error = service.register_user(test_db, "user@example.com", "password123")
        assert error is None
        
        # Second registration with same email fails
        user2, error = service.register_user(test_db, "user@example.com", "password456")
        assert error is not None
        assert user2 is None
    
    def test_register_user_invalid_email(self, test_db):
        """Invalid email rejected"""
        service = AuthService()
        
        user, error = service.register_user(test_db, "not-an-email", "password123")
        assert error is not None
        assert user is None
    
    def test_login_user(self, test_db):
        """User login returns token"""
        service = AuthService()
        
        # Register user
        service.register_user(test_db, "user@example.com", "password123")
        
        # Login
        token, error = service.login_user(test_db, "user@example.com", "password123")
        assert error is None
        assert token is not None
    
    def test_login_user_wrong_password(self, test_db):
        """Login with wrong password fails"""
        service = AuthService()
        
        # Register user
        service.register_user(test_db, "user@example.com", "password123")
        
        # Login with wrong password
        token, error = service.login_user(test_db, "user@example.com", "wrongpassword")
        assert error is not None
        assert token is None
    
    def test_login_user_nonexistent(self, test_db):
        """Login nonexistent user fails"""
        service = AuthService()
        
        token, error = service.login_user(test_db, "nonexistent@example.com", "password")
        assert error is not None
        assert token is None


class TestAuthRoutes:
    """Test API routes"""
    
    def test_register_route(self, client, test_db):
        """POST /api/auth/register"""
        response = client.post('/api/auth/register', json={
            "email": "newuser@example.com",
            "password": "password123"
        })
        
        assert response.status_code == 201
        data = response.get_json()
        assert data["success"] is True
        assert data["data"]["email"] == "newuser@example.com"
    
    def test_register_route_validation(self, client):
        """Register validates input"""
        # Missing email
        response = client.post('/api/auth/register', json={
            "password": "password123"
        })
        assert response.status_code == 400
        
        # Short password
        response = client.post('/api/auth/register', json={
            "email": "user@example.com",
            "password": "short"
        })
        assert response.status_code == 400
    
    def test_login_route(self, client, test_db):
        """POST /api/auth/login"""
        # Register first
        client.post('/api/auth/register', json={
            "email": "user@example.com",
            "password": "password123"
        })
        
        # Login
        response = client.post('/api/auth/login', json={
            "email": "user@example.com",
            "password": "password123"
        })
        
        assert response.status_code == 200
        data = response.get_json()
        assert data["success"] is True
        assert "token" in data["data"]
    
    def test_login_route_wrong_password(self, client, test_db):
        """Login rejects wrong password"""
        # Register first
        client.post('/api/auth/register', json={
            "email": "user@example.com",
            "password": "password123"
        })
        
        # Login with wrong password
        response = client.post('/api/auth/login', json={
            "email": "user@example.com",
            "password": "wrongpassword"
        })
        
        assert response.status_code == 401
        data = response.get_json()
        assert data["success"] is False
    
    def test_logout_route(self, client):
        """POST /api/auth/logout"""
        response = client.post('/api/auth/logout')
        assert response.status_code == 200
        assert response.get_json()["success"] is True
