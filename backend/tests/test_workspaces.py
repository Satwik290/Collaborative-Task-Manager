"""
Tests for workspace operations.
"""

import pytest
from auth_service import AuthService
from workspace_service import WorkspaceService
from models import User, Workspace, WorkspaceMember
import json


def create_user(db, email, password="password123"):
    """Helper: create and return user"""
    service = AuthService()
    user, _ = service.register_user(db, email, password)
    return user


def create_workspace_and_user(db):
    """Helper: create user and workspace"""
    user = create_user(db, "creator@example.com")
    workspace, _ = WorkspaceService.create_workspace(db, user.id, "Test Workspace")
    return user, workspace


class TestWorkspaceService:
    """Test workspace business logic"""
    
    def test_create_workspace(self, test_db):
        """Create workspace"""
        user = create_user(test_db, "user@example.com")
        
        workspace, error = WorkspaceService.create_workspace(test_db, user.id, "My Workspace")
        
        assert error is None
        assert workspace is not None
        assert workspace.name == "My Workspace"
        assert workspace.created_by == user.id
        
        # Creator is automatically admin
        member = test_db.query(WorkspaceMember).filter(
            WorkspaceMember.workspace_id == workspace.id,
            WorkspaceMember.user_id == user.id
        ).first()
        assert member is not None
        assert member.role == "admin"
    
    def test_get_user_workspaces(self, test_db):
        """List user's workspaces"""
        user1 = create_user(test_db, "user1@example.com")
        user2 = create_user(test_db, "user2@example.com")
        
        # Create 2 workspaces for user1
        ws1, _ = WorkspaceService.create_workspace(test_db, user1.id, "WS1")
        ws2, _ = WorkspaceService.create_workspace(test_db, user1.id, "WS2")
        
        # Add user2 to ws1
        WorkspaceService.add_member(test_db, ws1.id, user2.email, "member")
        
        # user1 sees 2 workspaces
        workspaces, error = WorkspaceService.get_user_workspaces(test_db, user1.id)
        assert error is None
        assert len(workspaces) == 2
        
        # user2 sees only ws1
        workspaces, error = WorkspaceService.get_user_workspaces(test_db, user2.id)
        assert error is None
        assert len(workspaces) == 1
    
    def test_is_member(self, test_db):
        """Check workspace membership"""
        user1 = create_user(test_db, "user1@example.com")
        user2 = create_user(test_db, "user2@example.com")
        workspace, _ = WorkspaceService.create_workspace(test_db, user1.id, "WS")
        
        # user1 is member (creator)
        assert WorkspaceService.is_member(test_db, user1.id, workspace.id)
        
        # user2 is not member
        assert not WorkspaceService.is_member(test_db, user2.id, workspace.id)
    
    def test_is_admin(self, test_db):
        """Check admin status"""
        user1 = create_user(test_db, "user1@example.com")
        user2 = create_user(test_db, "user2@example.com")
        workspace, _ = WorkspaceService.create_workspace(test_db, user1.id, "WS")
        
        # Add user2 as member (not admin)
        WorkspaceService.add_member(test_db, workspace.id, user2.email, "member")
        
        # user1 is admin
        assert WorkspaceService.is_admin(test_db, user1.id, workspace.id)
        
        # user2 is not admin
        assert not WorkspaceService.is_admin(test_db, user2.id, workspace.id)
    
    def test_add_member(self, test_db):
        """Add member to workspace"""
        user1 = create_user(test_db, "user1@example.com")
        user2 = create_user(test_db, "user2@example.com")
        workspace, _ = WorkspaceService.create_workspace(test_db, user1.id, "WS")
        
        # Add user2
        member, error = WorkspaceService.add_member(test_db, workspace.id, user2.email, "member")
        
        assert error is None
        assert member is not None
        assert member.user_id == user2.id
        assert member.role == "member"
    
    def test_add_member_duplicate(self, test_db):
        """Cannot add same user twice"""
        user1 = create_user(test_db, "user1@example.com")
        user2 = create_user(test_db, "user2@example.com")
        workspace, _ = WorkspaceService.create_workspace(test_db, user1.id, "WS")
        
        # Add user2
        WorkspaceService.add_member(test_db, workspace.id, user2.email, "member")
        
        # Try to add again
        member, error = WorkspaceService.add_member(test_db, workspace.id, user2.email, "admin")
        assert error is not None
        assert member is None
    
    def test_remove_member(self, test_db):
        """Remove member from workspace"""
        user1 = create_user(test_db, "user1@example.com")
        user2 = create_user(test_db, "user2@example.com")
        workspace, _ = WorkspaceService.create_workspace(test_db, user1.id, "WS")
        
        # Add and remove user2
        WorkspaceService.add_member(test_db, workspace.id, user2.email, "member")
        success, error = WorkspaceService.remove_member(test_db, workspace.id, user2.id)
        
        assert error is None
        assert success is True
        assert not WorkspaceService.is_member(test_db, user2.id, workspace.id)
    
    def test_cannot_remove_last_admin(self, test_db):
        """Cannot remove creator if they're last admin"""
        user1 = create_user(test_db, "user1@example.com")
        workspace, _ = WorkspaceService.create_workspace(test_db, user1.id, "WS")
        
        # Try to remove creator
        success, error = WorkspaceService.remove_member(test_db, workspace.id, user1.id)
        
        assert success is False
        assert error is not None
        assert "last admin" in error.lower()


class TestWorkspaceRoutes:
    """Test workspace API routes"""
    
    def get_token(self, client, email, password="password123"):
        """Helper: register and login user, return token"""
        client.post('/api/auth/register', json={
            "email": email,
            "password": password
        })
        response = client.post('/api/auth/login', json={
            "email": email,
            "password": password
        })
        return response.get_json()["data"]["token"]
    
    def test_create_workspace_route(self, client):
        """POST /api/workspaces"""
        token = self.get_token(client, "user@example.com")
        
        response = client.post(
            '/api/workspaces',
            json={"name": "My Workspace"},
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 201
        data = response.get_json()
        assert data["success"] is True
        assert data["data"]["name"] == "My Workspace"
    
    def test_list_workspaces_route(self, client):
        """GET /api/workspaces"""
        token = self.get_token(client, "user@example.com")
        
        # Create 2 workspaces
        client.post(
            '/api/workspaces',
            json={"name": "WS1"},
            headers={"Authorization": f"Bearer {token}"}
        )
        client.post(
            '/api/workspaces',
            json={"name": "WS2"},
            headers={"Authorization": f"Bearer {token}"}
        )
        
        # List
        response = client.get(
            '/api/workspaces',
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 200
        data = response.get_json()
        assert len(data["data"]) == 2
    
    def test_requires_auth(self, client):
        """Routes require authentication"""
        response = client.get('/api/workspaces')
        assert response.status_code == 401
    
    def test_invalid_token(self, client):
        """Invalid token rejected"""
        response = client.get(
            '/api/workspaces',
            headers={"Authorization": "Bearer invalid"}
        )
        assert response.status_code == 401
