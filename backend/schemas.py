"""
Request and response schemas.
Validate all inputs at API boundary.
"""

from typing import Optional, Dict, Any, List
from dataclasses import dataclass


# Request Schemas (incoming data)

@dataclass
class RegisterRequest:
    """POST /api/auth/register"""
    email: str
    password: str
    
    @staticmethod
    def from_json(data: Dict[str, Any]) -> tuple['RegisterRequest', Optional[str]]:
        """
        Parse and validate request data.
        Returns: (request_obj, error_message)
        """
        if not isinstance(data, dict):
            return None, "Request body must be JSON object"
        
        email = data.get("email", "").strip()
        password = data.get("password", "")
        
        if not email:
            return None, "email is required"
        if not password:
            return None, "password is required"
        
        if len(email) > 255:
            return None, "email must be less than 255 characters"
        if len(password) < 6:
            return None, "password must be at least 6 characters"
        if len(password) > 255:
            return None, "password must be less than 255 characters"
        
        return RegisterRequest(email=email, password=password), None


@dataclass
class LoginRequest:
    """POST /api/auth/login"""
    email: str
    password: str
    
    @staticmethod
    def from_json(data: Dict[str, Any]) -> tuple['LoginRequest', Optional[str]]:
        """Parse and validate login request"""
        if not isinstance(data, dict):
            return None, "Request body must be JSON object"
        
        email = data.get("email", "").strip()
        password = data.get("password", "")
        
        if not email:
            return None, "email is required"
        if not password:
            return None, "password is required"
        
        return LoginRequest(email=email, password=password), None


@dataclass
class CreateWorkspaceRequest:
    """POST /api/workspaces"""
    name: str
    
    @staticmethod
    def from_json(data: Dict[str, Any]) -> tuple['CreateWorkspaceRequest', Optional[str]]:
        """Parse and validate"""
        if not isinstance(data, dict):
            return None, "Request body must be JSON object"
        
        name = data.get("name", "").strip()
        
        if not name:
            return None, "name is required"
        if len(name) > 255:
            return None, "name must be less than 255 characters"
        
        return CreateWorkspaceRequest(name=name), None


@dataclass
class UpdateWorkspaceRequest:
    """PUT /api/workspaces/:id"""
    name: str
    
    @staticmethod
    def from_json(data: Dict[str, Any]) -> tuple['UpdateWorkspaceRequest', Optional[str]]:
        """Parse and validate"""
        if not isinstance(data, dict):
            return None, "Request body must be JSON object"
        
        name = data.get("name", "").strip()
        
        if not name:
            return None, "name is required"
        if len(name) > 255:
            return None, "name must be less than 255 characters"
        
        return UpdateWorkspaceRequest(name=name), None


@dataclass
class InviteMemberRequest:
    """POST /api/workspaces/:id/members"""
    email: str
    role: str
    
    @staticmethod
    def from_json(data: Dict[str, Any]) -> tuple['InviteMemberRequest', Optional[str]]:
        """Parse and validate"""
        if not isinstance(data, dict):
            return None, "Request body must be JSON object"
        
        email = data.get("email", "").strip()
        role = data.get("role", "").strip().lower()
        
        if not email:
            return None, "email is required"
        if not role:
            return None, "role is required"
        if role not in ["admin", "member"]:
            return None, "role must be 'admin' or 'member'"
        
        return InviteMemberRequest(email=email, role=role), None


@dataclass
class CreateTaskRequest:
    """POST /api/workspaces/:id/tasks"""
    title: str
    description: Optional[str]
    assigned_to: Optional[int]
    
    @staticmethod
    def from_json(data: Dict[str, Any]) -> tuple['CreateTaskRequest', Optional[str]]:
        """Parse and validate"""
        if not isinstance(data, dict):
            return None, "Request body must be JSON object"
        
        title = data.get("title", "").strip()
        description = data.get("description", "").strip() if data.get("description") else None
        assigned_to = data.get("assigned_to")
        
        if not title:
            return None, "title is required"
        if len(title) > 255:
            return None, "title must be less than 255 characters"
        
        if description and len(description) > 2000:
            return None, "description must be less than 2000 characters"
        
        if assigned_to is not None and not isinstance(assigned_to, int):
            return None, "assigned_to must be a user ID (integer)"
        
        return CreateTaskRequest(title=title, description=description, assigned_to=assigned_to), None


@dataclass
class UpdateTaskRequest:
    """PUT /api/workspaces/:id/tasks/:task_id"""
    title: Optional[str]
    description: Optional[str]
    status: Optional[str]
    assigned_to: Optional[int]
    
    @staticmethod
    def from_json(data: Dict[str, Any]) -> tuple['UpdateTaskRequest', Optional[str]]:
        """Parse and validate"""
        if not isinstance(data, dict):
            return None, "Request body must be JSON object"
        
        title = data.get("title")
        description = data.get("description")
        status = data.get("status")
        assigned_to = data.get("assigned_to")
        
        # All fields optional
        if title is not None:
            title = str(title).strip()
            if not title:
                return None, "title cannot be empty"
            if len(title) > 255:
                return None, "title must be less than 255 characters"
        
        if description is not None:
            description = str(description).strip()
            if len(description) > 2000:
                return None, "description must be less than 2000 characters"
        
        if status is not None:
            status = str(status).strip().lower()
            if status not in ["todo", "in_progress", "done"]:
                return None, "status must be 'todo', 'in_progress', or 'done'"
        
        if assigned_to is not None and not isinstance(assigned_to, int):
            return None, "assigned_to must be a user ID (integer)"
        
        return UpdateTaskRequest(title=title, description=description, status=status, assigned_to=assigned_to), None


@dataclass
class CommentRequest:
    """POST /api/workspaces/:id/tasks/:task_id/comments"""
    content: str
    
    @staticmethod
    def from_json(data: Dict[str, Any]) -> tuple['CommentRequest', Optional[str]]:
        """Parse and validate"""
        if not isinstance(data, dict):
            return None, "Request body must be JSON object"
        
        content = data.get("content", "").strip()
        
        if not content:
            return None, "content is required"
        if len(content) > 1000:
            return None, "content must be less than 1000 characters"
        
        return CommentRequest(content=content), None


# Response Schemas (outgoing data)

def success_response(data: Any = None) -> Dict[str, Any]:
    """Format successful response"""
    return {"success": True, "data": data}


def error_response(message: str, details: Dict[str, Any] = None) -> Dict[str, Any]:
    """Format error response"""
    response = {"success": False, "error": message}
    if details:
        response["details"] = details
    return response


def user_to_dict(user) -> Dict[str, Any]:
    """Convert User model to response dict"""
    return {
        "id": user.id,
        "email": user.email,
        "created_at": user.created_at.isoformat()
    }


def workspace_to_dict(workspace) -> Dict[str, Any]:
    """Convert Workspace model to response dict"""
    return {
        "id": workspace.id,
        "name": workspace.name,
        "created_by": workspace.created_by,
        "created_at": workspace.created_at.isoformat()
    }


def workspace_member_to_dict(member) -> Dict[str, Any]:
    """Convert WorkspaceMember model to response dict"""
    return {
        "user_id": member.user_id,
        "email": member.user.email,
        "role": member.role,
        "joined_at": member.joined_at.isoformat()
    }


def task_to_dict(task, include_comments: bool = False) -> Dict[str, Any]:
    """Convert Task model to response dict"""
    response = {
        "id": task.id,
        "workspace_id": task.workspace_id,
        "title": task.title,
        "description": task.description,
        "status": task.status,
        "assigned_to": task.assigned_to,
        "created_by": task.created_by,
        "created_at": task.created_at.isoformat(),
        "updated_at": task.updated_at.isoformat()
    }
    
    if include_comments:
        response["comments"] = [comment_to_dict(c) for c in task.comments]
    
    return response


def comment_to_dict(comment) -> Dict[str, Any]:
    """Convert TaskComment model to response dict"""
    return {
        "id": comment.id,
        "task_id": comment.task_id,
        "user_id": comment.user_id,
        "email": comment.author.email,
        "content": comment.content,
        "created_at": comment.created_at.isoformat()
    }
