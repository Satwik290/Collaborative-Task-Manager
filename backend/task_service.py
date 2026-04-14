"""
Task service.
Business logic for task CRUD operations.
"""

from datetime import datetime
from typing import Optional, List, Tuple
from sqlalchemy.orm import Session
from models import Task, TaskComment, WorkspaceMember


class TaskService:
    """
    Business logic for tasks.
    All methods return (result, error) tuples.
    """
    
    @staticmethod
    def create_task(
        db: Session,
        workspace_id: int,
        created_by: int,
        title: str,
        description: Optional[str] = None,
        priority: str = "medium",
        due_date: Optional[str] = None,
        assigned_to: Optional[int] = None
    ) -> Tuple[Optional[Task], Optional[str]]:
        """
        Create a new task in workspace.
        
        Args:
            db: Database session
            workspace_id: Workspace ID
            created_by: User creating task
            title: Task title
            description: Task description (optional)
            assigned_to: User ID to assign to (optional)
        
        Returns:
            (Task, error_message)
        """
        if not title:
            return None, "title is required"
        
        try:
            # Verify assigned_to user is member if provided
            if assigned_to:
                member = db.query(WorkspaceMember).filter(
                    WorkspaceMember.workspace_id == workspace_id,
                    WorkspaceMember.user_id == assigned_to
                ).first()
                if not member:
                    return None, "Assigned user is not member of this workspace"
            
            # Parse due_date
            parsed_due_date = None
            if due_date:
                try:
                    parsed_due_date = datetime.fromisoformat(due_date.replace('Z', '+00:00'))
                except ValueError:
                    return None, "Invalid due_date format (ISO 8601 expected)"
            
            task = Task(
                workspace_id=workspace_id,
                created_by=created_by,
                title=title,
                description=description,
                priority=priority,
                due_date=parsed_due_date,
                assigned_to=assigned_to,
                status="todo"
            )
            db.add(task)
            db.commit()
            db.refresh(task)
            return task, None
        except Exception as e:
            db.rollback()
            return None, f"Failed to create task: {str(e)}"
    
    @staticmethod
    def get_task(db: Session, task_id: int) -> Tuple[Optional[Task], Optional[str]]:
        """
        Get task by ID.
        Caller must verify workspace membership.
        """
        try:
            task = db.query(Task).filter(Task.id == task_id).first()
            if not task:
                return None, "Task not found"
            return task, None
        except Exception as e:
            return None, f"Failed to fetch task: {str(e)}"
    
    @staticmethod
    def get_workspace_tasks(db: Session, workspace_id: int) -> Tuple[Optional[List[Task]], Optional[str]]:
        """
        Get all tasks in workspace.
        Caller must verify workspace membership.
        """
        try:
            tasks = db.query(Task).filter(Task.workspace_id == workspace_id).all()
            return tasks, None
        except Exception as e:
            return None, f"Failed to fetch tasks: {str(e)}"
    
    @staticmethod
    def update_task(
        db: Session,
        task_id: int,
        title: Optional[str] = None,
        description: Optional[str] = None,
        status: Optional[str] = None,
        priority: Optional[str] = None,
        due_date: Optional[str] = None,
        assigned_to: Optional[int] = None
    ) -> Tuple[Optional[Task], Optional[str]]:
        """
        Update task fields.
        All fields optional (only update provided ones).
        Caller must verify permissions.
        
        Args:
            db: Database session
            task_id: Task ID
            title: New title (or None to skip)
            description: New description (or None to skip)
            status: New status (or None to skip)
            assigned_to: Assign to user (or None to skip)
        
        Returns:
            (Task, error_message)
        """
        try:
            task = db.query(Task).filter(Task.id == task_id).first()
            if not task:
                return None, "Task not found"
            
            # Verify assigned_to is member if provided
            if assigned_to is not None:
                member = db.query(WorkspaceMember).filter(
                    WorkspaceMember.workspace_id == task.workspace_id,
                    WorkspaceMember.user_id == assigned_to
                ).first()
                if not member:
                    return None, "Assigned user is not member of this workspace"
            
            # Update fields
            if title is not None:
                task.title = title
            if description is not None:
                task.description = description
            if status is not None:
                task.status = status
            if priority is not None:
                task.priority = priority
            if due_date is not None:
                if due_date == "":
                    task.due_date = None
                else:
                    try:
                        task.due_date = datetime.fromisoformat(due_date.replace('Z', '+00:00'))
                    except ValueError:
                        return None, "Invalid due_date format (ISO 8601 expected)"
            if assigned_to is not None:
                task.assigned_to = assigned_to
            
            db.commit()
            db.refresh(task)
            return task, None
        except Exception as e:
            db.rollback()
            return None, f"Failed to update task: {str(e)}"
    
    @staticmethod
    def delete_task(db: Session, task_id: int) -> Tuple[bool, Optional[str]]:
        """
        Delete task (and all its comments via cascade).
        Caller must verify permissions.
        """
        try:
            task = db.query(Task).filter(Task.id == task_id).first()
            if not task:
                return False, "Task not found"
            
            db.delete(task)
            db.commit()
            return True, None
        except Exception as e:
            db.rollback()
            return False, f"Failed to delete task: {str(e)}"
    
    @staticmethod
    def add_comment(
        db: Session,
        task_id: int,
        user_id: int,
        content: str
    ) -> Tuple[Optional[TaskComment], Optional[str]]:
        """
        Add comment to task.
        Caller must verify workspace membership and task access.
        """
        if not content:
            return None, "content is required"
        
        try:
            task = db.query(Task).filter(Task.id == task_id).first()
            if not task:
                return None, "Task not found"
            
            comment = TaskComment(task_id=task_id, user_id=user_id, content=content)
            db.add(comment)
            db.commit()
            db.refresh(comment)
            return comment, None
        except Exception as e:
            db.rollback()
            return None, f"Failed to add comment: {str(e)}"
    
    @staticmethod
    def get_task_comments(db: Session, task_id: int) -> Tuple[Optional[List[TaskComment]], Optional[str]]:
        """
        Get all comments on task.
        Caller must verify task access.
        """
        try:
            comments = db.query(TaskComment).filter(TaskComment.task_id == task_id).all()
            return comments, None
        except Exception as e:
            return None, f"Failed to fetch comments: {str(e)}"
    
    @staticmethod
    def delete_comment(db: Session, comment_id: int) -> Tuple[bool, Optional[str]]:
        """
        Delete comment.
        Caller must verify comment ownership.
        """
        try:
            comment = db.query(TaskComment).filter(TaskComment.id == comment_id).first()
            if not comment:
                return False, "Comment not found"
            
            db.delete(comment)
            db.commit()
            return True, None
        except Exception as e:
            db.rollback()
            return False, f"Failed to delete comment: {str(e)}"
