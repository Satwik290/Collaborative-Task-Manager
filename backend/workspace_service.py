"""
Workspace service.
Pure business logic for workspace operations.
No Flask or HTTP concerns.
"""

from typing import Optional, List, Tuple
from sqlalchemy.orm import Session
from models import Workspace, WorkspaceMember, User, Task


class WorkspaceService:
    """
    Business logic for workspace operations.
    All methods return (result, error_message) tuples.
    """
    
    @staticmethod
    def create_workspace(db: Session, user_id: int, name: str) -> Tuple[Optional[Workspace], Optional[str]]:
        """
        Create a new workspace.
        Creator becomes admin.
        
        Args:
            db: Database session
            user_id: User creating workspace
            name: Workspace name
        
        Returns:
            (Workspace object, error_message)
        """
        if not user_id or not name:
            return None, "user_id and name required"
        
        try:
            workspace = Workspace(name=name, created_by=user_id)
            db.add(workspace)
            db.flush()  # Flush to get workspace.id
            
            # Add creator as admin member
            member = WorkspaceMember(workspace_id=workspace.id, user_id=user_id, role="admin")
            db.add(member)
            db.commit()
            db.refresh(workspace)
            return workspace, None
        except Exception as e:
            db.rollback()
            return None, f"Failed to create workspace: {str(e)}"
    
    @staticmethod
    def get_user_workspaces(db: Session, user_id: int) -> Tuple[Optional[List[Workspace]], Optional[str]]:
        """
        Get all workspaces user is member of.
        """
        try:
            workspaces = db.query(Workspace).join(
                WorkspaceMember,
                Workspace.id == WorkspaceMember.workspace_id
            ).filter(
                WorkspaceMember.user_id == user_id
            ).all()
            return workspaces, None
        except Exception as e:
            return None, f"Failed to fetch workspaces: {str(e)}"
    
    @staticmethod
    def get_workspace(db: Session, workspace_id: int) -> Tuple[Optional[Workspace], Optional[str]]:
        """
        Get workspace by ID.
        """
        try:
            workspace = db.query(Workspace).filter(Workspace.id == workspace_id).first()
            if not workspace:
                return None, "Workspace not found"
            return workspace, None
        except Exception as e:
            return None, f"Failed to fetch workspace: {str(e)}"
    
    @staticmethod
    def update_workspace(db: Session, workspace_id: int, name: str) -> Tuple[Optional[Workspace], Optional[str]]:
        """
        Update workspace name.
        Caller must have checked admin permission.
        """
        if not name:
            return None, "name is required"
        
        try:
            workspace = db.query(Workspace).filter(Workspace.id == workspace_id).first()
            if not workspace:
                return None, "Workspace not found"
            
            workspace.name = name
            db.commit()
            db.refresh(workspace)
            return workspace, None
        except Exception as e:
            db.rollback()
            return None, f"Failed to update workspace: {str(e)}"
    
    @staticmethod
    def delete_workspace(db: Session, workspace_id: int) -> Tuple[bool, Optional[str]]:
        """
        Delete workspace and all related data.
        Caller must have checked admin permission.
        """
        try:
            workspace = db.query(Workspace).filter(Workspace.id == workspace_id).first()
            if not workspace:
                return False, "Workspace not found"
            
            db.delete(workspace)
            db.commit()
            return True, None
        except Exception as e:
            db.rollback()
            return False, f"Failed to delete workspace: {str(e)}"
    
    @staticmethod
    def is_member(db: Session, user_id: int, workspace_id: int) -> bool:
        """
        Check if user is member of workspace.
        """
        member = db.query(WorkspaceMember).filter(
            WorkspaceMember.user_id == user_id,
            WorkspaceMember.workspace_id == workspace_id
        ).first()
        return member is not None
    
    @staticmethod
    def is_admin(db: Session, user_id: int, workspace_id: int) -> bool:
        """
        Check if user is admin of workspace.
        """
        member = db.query(WorkspaceMember).filter(
            WorkspaceMember.user_id == user_id,
            WorkspaceMember.workspace_id == workspace_id
        ).first()
        return member is not None and member.role == "admin"
    
    @staticmethod
    def get_members(db: Session, workspace_id: int) -> Tuple[Optional[List[WorkspaceMember]], Optional[str]]:
        """
        Get all members of workspace.
        Caller must have verified membership.
        """
        try:
            members = db.query(WorkspaceMember).filter(
                WorkspaceMember.workspace_id == workspace_id
            ).all()
            return members, None
        except Exception as e:
            return None, f"Failed to fetch members: {str(e)}"
    
    @staticmethod
    def add_member(db: Session, workspace_id: int, email: str, role: str) -> Tuple[Optional[WorkspaceMember], Optional[str]]:
        """
        Invite user to workspace by email.
        Caller must have checked admin permission.
        
        Args:
            db: Database session
            workspace_id: Target workspace
            email: Email of user to invite
            role: 'admin' or 'member'
        
        Returns:
            (WorkspaceMember, error_message)
        """
        if role not in ["admin", "member"]:
            return None, "role must be 'admin' or 'member'"
        
        try:
            # Find user by email
            user = db.query(User).filter(User.email == email).first()
            if not user:
                return None, f"User with email '{email}' not found"
            
            # Check if already member
            existing = db.query(WorkspaceMember).filter(
                WorkspaceMember.workspace_id == workspace_id,
                WorkspaceMember.user_id == user.id
            ).first()
            if existing:
                return None, "User is already member of this workspace"
            
            # Add member
            member = WorkspaceMember(workspace_id=workspace_id, user_id=user.id, role=role)
            db.add(member)
            db.commit()
            db.refresh(member)
            return member, None
        except Exception as e:
            db.rollback()
            return None, f"Failed to add member: {str(e)}"
    
    @staticmethod
    def remove_member(db: Session, workspace_id: int, user_id: int) -> Tuple[bool, Optional[str]]:
        """
        Remove member from workspace.
        Caller must have checked admin permission.
        Cannot remove creator (last admin).
        """
        try:
            member = db.query(WorkspaceMember).filter(
                WorkspaceMember.workspace_id == workspace_id,
                WorkspaceMember.user_id == user_id
            ).first()
            if not member:
                return False, "Member not found in workspace"
            
            # Prevent removing last admin
            workspace = db.query(Workspace).filter(Workspace.id == workspace_id).first()
            if member.role == "admin" and workspace.created_by == user_id:
                admin_count = db.query(WorkspaceMember).filter(
                    WorkspaceMember.workspace_id == workspace_id,
                    WorkspaceMember.role == "admin"
                ).count()
                if admin_count <= 1:
                    return False, "Cannot remove the workspace creator (last admin)"
            
            db.delete(member)
            db.commit()
            return True, None
        except Exception as e:
            db.rollback()
            return False, f"Failed to remove member: {str(e)}"
