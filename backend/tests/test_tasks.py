"""
Tests for task operations and permissions.
"""

import pytest
from auth_service import AuthService
from workspace_service import WorkspaceService
from task_service import TaskService
from models import User, Workspace, Task
import json


def create_user(db, email, password="password123"):
    """Helper: create user"""
    service = AuthService()
    user, _ = service.register_user(db, email, password)
    return user


def create_workspace_with_members(db):
    """Helper: create workspace with 2 members"""
    user1 = create_user(db, "admin@example.com")
    user2 = create_user(db, "member@example.com")
    
    workspace, _ = WorkspaceService.create_workspace(db, user1.id, "Test WS")
    WorkspaceService.add_member(db, workspace.id, user2.email, "member")
    
    return workspace, user1, user2


class TestTaskService:
    """Test task business logic"""
    
    def test_create_task(self, test_db):
        """Create task in workspace"""
        workspace, user1, user2 = create_workspace_with_members(test_db)
        
        task, error = TaskService.create_task(
            test_db, workspace.id, user1.id, "Buy milk"
        )
        
        assert error is None
        assert task is not None
        assert task.title == "Buy milk"
        assert task.status == "todo"
        assert task.created_by == user1.id
    
    def test_create_task_with_assignment(self, test_db):
        """Create task and assign to member"""
        workspace, user1, user2 = create_workspace_with_members(test_db)
        
        task, error = TaskService.create_task(
            test_db, workspace.id, user1.id, "Review PR",
            assigned_to=user2.id
        )
        
        assert error is None
        assert task.assigned_to == user2.id
    
    def test_create_task_assign_nonmember_fails(self, test_db):
        """Cannot assign task to non-member"""
        workspace, user1, user2 = create_workspace_with_members(test_db)
        user3 = create_user(test_db, "outsider@example.com")
        
        task, error = TaskService.create_task(
            test_db, workspace.id, user1.id, "Task",
            assigned_to=user3.id
        )
        
        assert error is not None
        assert task is None
    
    def test_get_task(self, test_db):
        """Retrieve task by ID"""
        workspace, user1, user2 = create_workspace_with_members(test_db)
        
        task, _ = TaskService.create_task(test_db, workspace.id, user1.id, "Task 1")
        retrieved, error = TaskService.get_task(test_db, task.id)
        
        assert error is None
        assert retrieved.id == task.id
    
    def test_get_nonexistent_task(self, test_db):
        """Getting nonexistent task fails gracefully"""
        task, error = TaskService.get_task(test_db, 999)
        
        assert error is not None
        assert task is None
    
    def test_get_workspace_tasks(self, test_db):
        """List all tasks in workspace"""
        workspace, user1, user2 = create_workspace_with_members(test_db)
        
        # Create 3 tasks
        TaskService.create_task(test_db, workspace.id, user1.id, "Task 1")
        TaskService.create_task(test_db, workspace.id, user2.id, "Task 2")
        TaskService.create_task(test_db, workspace.id, user1.id, "Task 3")
        
        tasks, error = TaskService.get_workspace_tasks(test_db, workspace.id)
        
        assert error is None
        assert len(tasks) == 3
    
    def test_update_task_status(self, test_db):
        """Update task status"""
        workspace, user1, user2 = create_workspace_with_members(test_db)
        task, _ = TaskService.create_task(test_db, workspace.id, user1.id, "Task")
        
        updated, error = TaskService.update_task(test_db, task.id, status="in_progress")
        
        assert error is None
        assert updated.status == "in_progress"
    
    def test_update_task_multiple_fields(self, test_db):
        """Update multiple fields at once"""
        workspace, user1, user2 = create_workspace_with_members(test_db)
        task, _ = TaskService.create_task(test_db, workspace.id, user1.id, "Old Title")
        
        updated, error = TaskService.update_task(
            test_db, task.id,
            title="New Title",
            description="New description",
            status="done",
            assigned_to=user2.id
        )
        
        assert error is None
        assert updated.title == "New Title"
        assert updated.description == "New description"
        assert updated.status == "done"
        assert updated.assigned_to == user2.id
    
    def test_update_task_partial(self, test_db):
        """Only update fields that are provided"""
        workspace, user1, user2 = create_workspace_with_members(test_db)
        task, _ = TaskService.create_task(
            test_db, workspace.id, user1.id, "Title",
            description="Original"
        )
        
        # Only update title
        updated, error = TaskService.update_task(test_db, task.id, title="New Title")
        
        assert error is None
        assert updated.title == "New Title"
        assert updated.description == "Original"  # Unchanged
    
    def test_delete_task(self, test_db):
        """Delete task"""
        workspace, user1, user2 = create_workspace_with_members(test_db)
        task, _ = TaskService.create_task(test_db, workspace.id, user1.id, "Task")
        
        success, error = TaskService.delete_task(test_db, task.id)
        
        assert error is None
        assert success is True
        
        # Verify deleted
        retrieved, _ = TaskService.get_task(test_db, task.id)
        assert retrieved is None
    
    def test_delete_task_cascade_deletes_comments(self, test_db):
        """Deleting task deletes its comments (cascade)"""
        workspace, user1, user2 = create_workspace_with_members(test_db)
        task, _ = TaskService.create_task(test_db, workspace.id, user1.id, "Task")
        
        # Add comments
        TaskService.add_comment(test_db, task.id, user1.id, "Comment 1")
        TaskService.add_comment(test_db, task.id, user2.id, "Comment 2")
        
        comments, _ = TaskService.get_task_comments(test_db, task.id)
        assert len(comments) == 2
        
        # Delete task
        TaskService.delete_task(test_db, task.id)
        
        # Verify comments gone
        comments, _ = TaskService.get_task_comments(test_db, task.id)
        assert len(comments) == 0
    
    def test_add_comment(self, test_db):
        """Add comment to task"""
        workspace, user1, user2 = create_workspace_with_members(test_db)
        task, _ = TaskService.create_task(test_db, workspace.id, user1.id, "Task")
        
        comment, error = TaskService.add_comment(
            test_db, task.id, user2.id, "Great work!"
        )
        
        assert error is None
        assert comment is not None
        assert comment.content == "Great work!"
        assert comment.user_id == user2.id
    
    def test_get_task_comments(self, test_db):
        """List comments on task"""
        workspace, user1, user2 = create_workspace_with_members(test_db)
        task, _ = TaskService.create_task(test_db, workspace.id, user1.id, "Task")
        
        TaskService.add_comment(test_db, task.id, user1.id, "Comment 1")
        TaskService.add_comment(test_db, task.id, user2.id, "Comment 2")
        
        comments, error = TaskService.get_task_comments(test_db, task.id)
        
        assert error is None
        assert len(comments) == 2
    
    def test_delete_comment(self, test_db):
        """Delete comment"""
        workspace, user1, user2 = create_workspace_with_members(test_db)
        task, _ = TaskService.create_task(test_db, workspace.id, user1.id, "Task")
        
        comment, _ = TaskService.add_comment(test_db, task.id, user1.id, "Comment")
        
        success, error = TaskService.delete_comment(test_db, comment.id)
        
        assert error is None
        assert success is True


class TestTaskRoutes:
    """Test task API routes"""
    
    def get_token(self, client, email, password="password123"):
        """Helper: register and login user"""
        client.post('/api/auth/register', json={
            "email": email,
            "password": password
        })
        response = client.post('/api/auth/login', json={
            "email": email,
            "password": password
        })
        return response.get_json()["data"]["token"]
    
    def create_workspace_via_api(self, client, token, name="Test WS"):
        """Helper: create workspace via API"""
        response = client.post(
            '/api/workspaces',
            json={"name": name},
            headers={"Authorization": f"Bearer {token}"}
        )
        return response.get_json()["data"]["id"]
    
    def test_create_task_route(self, client):
        """POST /api/workspaces/:id/tasks"""
        token = self.get_token(client, "user@example.com")
        ws_id = self.create_workspace_via_api(client, token)
        
        response = client.post(
            f'/api/workspaces/{ws_id}/tasks',
            json={"title": "Buy milk", "description": "Whole milk"},
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 201
        data = response.get_json()["data"]
        assert data["title"] == "Buy milk"
        assert data["status"] == "todo"
    
    def test_create_task_requires_title(self, client):
        """Task creation validates required fields"""
        token = self.get_token(client, "user@example.com")
        ws_id = self.create_workspace_via_api(client, token)
        
        response = client.post(
            f'/api/workspaces/{ws_id}/tasks',
            json={},
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 400
    
    def test_list_tasks_route(self, client):
        """GET /api/workspaces/:id/tasks"""
        token = self.get_token(client, "user@example.com")
        ws_id = self.create_workspace_via_api(client, token)
        
        # Create 2 tasks
        client.post(
            f'/api/workspaces/{ws_id}/tasks',
            json={"title": "Task 1"},
            headers={"Authorization": f"Bearer {token}"}
        )
        client.post(
            f'/api/workspaces/{ws_id}/tasks',
            json={"title": "Task 2"},
            headers={"Authorization": f"Bearer {token}"}
        )
        
        # List
        response = client.get(
            f'/api/workspaces/{ws_id}/tasks',
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 200
        data = response.get_json()["data"]
        assert len(data) == 2
    
    def test_get_task_route(self, client):
        """GET /api/workspaces/:id/tasks/:task_id"""
        token = self.get_token(client, "user@example.com")
        ws_id = self.create_workspace_via_api(client, token)
        
        # Create task
        create_resp = client.post(
            f'/api/workspaces/{ws_id}/tasks',
            json={"title": "Task"},
            headers={"Authorization": f"Bearer {token}"}
        )
        task_id = create_resp.get_json()["data"]["id"]
        
        # Get task
        response = client.get(
            f'/api/workspaces/{ws_id}/tasks/{task_id}',
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 200
        assert response.get_json()["data"]["title"] == "Task"
    
    def test_update_task_route(self, client):
        """PUT /api/workspaces/:id/tasks/:task_id"""
        token = self.get_token(client, "user@example.com")
        ws_id = self.create_workspace_via_api(client, token)
        
        # Create task
        create_resp = client.post(
            f'/api/workspaces/{ws_id}/tasks',
            json={"title": "Old"},
            headers={"Authorization": f"Bearer {token}"}
        )
        task_id = create_resp.get_json()["data"]["id"]
        
        # Update
        response = client.put(
            f'/api/workspaces/{ws_id}/tasks/{task_id}',
            json={"title": "New", "status": "done"},
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 200
        data = response.get_json()["data"]
        assert data["title"] == "New"
        assert data["status"] == "done"
    
    def test_delete_task_route(self, client):
        """DELETE /api/workspaces/:id/tasks/:task_id"""
        token = self.get_token(client, "user@example.com")
        ws_id = self.create_workspace_via_api(client, token)
        
        # Create task
        create_resp = client.post(
            f'/api/workspaces/{ws_id}/tasks',
            json={"title": "Task"},
            headers={"Authorization": f"Bearer {token}"}
        )
        task_id = create_resp.get_json()["data"]["id"]
        
        # Delete
        response = client.delete(
            f'/api/workspaces/{ws_id}/tasks/{task_id}',
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 200
        
        # Verify deleted
        get_resp = client.get(
            f'/api/workspaces/{ws_id}/tasks/{task_id}',
            headers={"Authorization": f"Bearer {token}"}
        )
        assert get_resp.status_code == 404
    
    def test_add_comment_route(self, client):
        """POST /api/workspaces/:id/tasks/:task_id/comments"""
        token = self.get_token(client, "user@example.com")
        ws_id = self.create_workspace_via_api(client, token)
        
        # Create task
        create_resp = client.post(
            f'/api/workspaces/{ws_id}/tasks',
            json={"title": "Task"},
            headers={"Authorization": f"Bearer {token}"}
        )
        task_id = create_resp.get_json()["data"]["id"]
        
        # Add comment
        response = client.post(
            f'/api/workspaces/{ws_id}/tasks/{task_id}/comments',
            json={"content": "Great!"},
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 201
        assert response.get_json()["data"]["content"] == "Great!"
    
    def test_list_comments_route(self, client):
        """GET /api/workspaces/:id/tasks/:task_id/comments"""
        token = self.get_token(client, "user@example.com")
        ws_id = self.create_workspace_via_api(client, token)
        
        # Create task
        create_resp = client.post(
            f'/api/workspaces/{ws_id}/tasks',
            json={"title": "Task"},
            headers={"Authorization": f"Bearer {token}"}
        )
        task_id = create_resp.get_json()["data"]["id"]
        
        # Add comments
        client.post(
            f'/api/workspaces/{ws_id}/tasks/{task_id}/comments',
            json={"content": "Comment 1"},
            headers={"Authorization": f"Bearer {token}"}
        )
        client.post(
            f'/api/workspaces/{ws_id}/tasks/{task_id}/comments',
            json={"content": "Comment 2"},
            headers={"Authorization": f"Bearer {token}"}
        )
        
        # List
        response = client.get(
            f'/api/workspaces/{ws_id}/tasks/{task_id}/comments',
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 200
        data = response.get_json()["data"]
        assert len(data) == 2
    
    def test_permission_denied_for_nonmember(self, client):
        """Non-members cannot access workspace tasks"""
        token1 = self.get_token(client, "user1@example.com")
        token2 = self.get_token(client, "user2@example.com")
        
        ws_id = self.create_workspace_via_api(client, token1)
        
        # user2 tries to access user1's workspace
        response = client.get(
            f'/api/workspaces/{ws_id}/tasks',
            headers={"Authorization": f"Bearer {token2}"}
        )
        
        assert response.status_code == 403
    
    def test_only_creator_or_admin_can_delete_task(self, client):
        """Task deletion restricted to creator/admin"""
        token1 = self.get_token(client, "admin@example.com")
        token2 = self.get_token(client, "member@example.com")
        
        ws_id = self.create_workspace_via_api(client, token1)
        
        # Add token2 as member (not admin)
        client.post(
            f'/api/workspaces/{ws_id}/members',
            json={"email": "member@example.com", "role": "member"},
            headers={"Authorization": f"Bearer {token1}"}
        )
        
        # token1 creates task
        create_resp = client.post(
            f'/api/workspaces/{ws_id}/tasks',
            json={"title": "Task"},
            headers={"Authorization": f"Bearer {token1}"}
        )
        task_id = create_resp.get_json()["data"]["id"]
        
        # token2 (non-creator, non-admin) tries to delete
        response = client.delete(
            f'/api/workspaces/{ws_id}/tasks/{task_id}',
            headers={"Authorization": f"Bearer {token2}"}
        )
        
        assert response.status_code == 403
