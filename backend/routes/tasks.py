"""
Task routes.
GET    /api/workspaces/:id/tasks
POST   /api/workspaces/:id/tasks
GET    /api/workspaces/:id/tasks/:task_id
PUT    /api/workspaces/:id/tasks/:task_id
DELETE /api/workspaces/:id/tasks/:task_id
GET    /api/workspaces/:id/tasks/:task_id/comments
POST   /api/workspaces/:id/tasks/:task_id/comments
DELETE /api/workspaces/:id/tasks/:task_id/comments/:comment_id
"""

from flask import Blueprint, request, jsonify
from database import get_db
from auth_middleware import require_auth
from workspace_service import WorkspaceService
from task_service import TaskService
from schemas import (
    CreateTaskRequest, UpdateTaskRequest, CommentRequest,
    success_response, error_response, task_to_dict, comment_to_dict
)

tasks_bp = Blueprint('tasks', __name__)


@tasks_bp.route('/api/workspaces/<int:workspace_id>/tasks', methods=['GET'])
@require_auth
def list_tasks(user_id, workspace_id):
    """
    List all tasks in workspace (user must be member).
    """
    db = get_db()
    
    # Check membership
    is_member = WorkspaceService.is_member(db, user_id, workspace_id)
    if not is_member:
        db.close()
        return jsonify(error_response("Not member of this workspace")), 403
    
    # Get tasks
    tasks, error = TaskService.get_workspace_tasks(db, workspace_id)
    db.close()
    
    if error:
        return jsonify(error_response(error)), 500
    
    data = [task_to_dict(t) for t in tasks]
    return jsonify(success_response(data)), 200


@tasks_bp.route('/api/workspaces/<int:workspace_id>/tasks', methods=['POST'])
@require_auth
def create_task(user_id, workspace_id):
    """
    Create task in workspace (user must be member).
    """
    db = get_db()
    
    # Check membership
    is_member = WorkspaceService.is_member(db, user_id, workspace_id)
    if not is_member:
        db.close()
        return jsonify(error_response("Not member of this workspace")), 403
    
    # Parse request
    data = request.get_json(silent=True) or {}
    req, error = CreateTaskRequest.from_json(data)
    if error:
        db.close()
        return jsonify(error_response(error)), 400
    
    # Create task
    task, error = TaskService.create_task(
        db, workspace_id, user_id, req.title, req.description, req.assigned_to
    )
    db.close()
    
    if error:
        return jsonify(error_response(error)), 400
    
    return jsonify(success_response(task_to_dict(task))), 201


@tasks_bp.route('/api/workspaces/<int:workspace_id>/tasks/<int:task_id>', methods=['GET'])
@require_auth
def get_task(user_id, workspace_id, task_id):
    """
    Get task details (user must be member of workspace).
    """
    db = get_db()
    
    # Check membership
    is_member = WorkspaceService.is_member(db, user_id, workspace_id)
    if not is_member:
        db.close()
        return jsonify(error_response("Not member of this workspace")), 403
    
    # Get task
    task, error = TaskService.get_task(db, task_id)
    
    if error:
        db.close()
        return jsonify(error_response(error)), 404
    
    # Verify task is in workspace
    if task.workspace_id != workspace_id:
        db.close()
        return jsonify(error_response("Task not found in this workspace")), 404
    
    data = task_to_dict(task, include_comments=True)
    db.close()
    return jsonify(success_response(data)), 200


@tasks_bp.route('/api/workspaces/<int:workspace_id>/tasks/<int:task_id>', methods=['PUT'])
@require_auth
def update_task(user_id, workspace_id, task_id):
    """
    Update task (any workspace member can update).
    """
    db = get_db()
    
    # Check membership
    is_member = WorkspaceService.is_member(db, user_id, workspace_id)
    if not is_member:
        db.close()
        return jsonify(error_response("Not member of this workspace")), 403
    
    # Verify task is in workspace
    task, error = TaskService.get_task(db, task_id)
    if error or task.workspace_id != workspace_id:
        db.close()
        return jsonify(error_response("Task not found in this workspace")), 404
    
    # Parse request
    data = request.get_json(silent=True) or {}
    req, error = UpdateTaskRequest.from_json(data)
    if error:
        db.close()
        return jsonify(error_response(error)), 400
    
    # Update task
    updated_task, error = TaskService.update_task(
        db, task_id, req.title, req.description, req.status, req.assigned_to
    )
    db.close()
    
    if error:
        return jsonify(error_response(error)), 400
    
    return jsonify(success_response(task_to_dict(updated_task))), 200


@tasks_bp.route('/api/workspaces/<int:workspace_id>/tasks/<int:task_id>', methods=['DELETE'])
@require_auth
def delete_task(user_id, workspace_id, task_id):
    """
    Delete task (creator or admin only).
    """
    db = get_db()
    
    # Check membership
    is_member = WorkspaceService.is_member(db, user_id, workspace_id)
    if not is_member:
        db.close()
        return jsonify(error_response("Not member of this workspace")), 403
    
    # Get task
    task, error = TaskService.get_task(db, task_id)
    if error or task.workspace_id != workspace_id:
        db.close()
        return jsonify(error_response("Task not found in this workspace")), 404
    
    # Check permission (creator or admin)
    is_creator = task.created_by == user_id
    is_admin = WorkspaceService.is_admin(db, user_id, workspace_id)
    
    if not (is_creator or is_admin):
        db.close()
        return jsonify(error_response("Permission denied")), 403
    
    # Delete task
    success, error = TaskService.delete_task(db, task_id)
    db.close()
    
    if error:
        return jsonify(error_response(error)), 500
    
    return jsonify(success_response()), 200


@tasks_bp.route('/api/workspaces/<int:workspace_id>/tasks/<int:task_id>/comments', methods=['GET'])
@require_auth
def list_comments(user_id, workspace_id, task_id):
    """
    List comments on task (user must be workspace member).
    """
    db = get_db()
    
    # Check membership
    is_member = WorkspaceService.is_member(db, user_id, workspace_id)
    if not is_member:
        db.close()
        return jsonify(error_response("Not member of this workspace")), 403
    
    # Verify task is in workspace
    task, error = TaskService.get_task(db, task_id)
    if error or task.workspace_id != workspace_id:
        db.close()
        return jsonify(error_response("Task not found in this workspace")), 404
    
    # Get comments
    comments, error = TaskService.get_task_comments(db, task_id)
    
    if error:
        db.close()
        return jsonify(error_response(error)), 500
    
    data = [comment_to_dict(c) for c in comments]
    db.close()
    return jsonify(success_response(data)), 200


@tasks_bp.route('/api/workspaces/<int:workspace_id>/tasks/<int:task_id>/comments', methods=['POST'])
@require_auth
def add_comment(user_id, workspace_id, task_id):
    """
    Add comment to task (user must be workspace member).
    """
    db = get_db()
    
    # Check membership
    is_member = WorkspaceService.is_member(db, user_id, workspace_id)
    if not is_member:
        db.close()
        return jsonify(error_response("Not member of this workspace")), 403
    
    # Verify task is in workspace
    task, error = TaskService.get_task(db, task_id)
    if error or task.workspace_id != workspace_id:
        db.close()
        return jsonify(error_response("Task not found in this workspace")), 404
    
    # Parse request
    data = request.get_json(silent=True) or {}
    req, error = CommentRequest.from_json(data)
    if error:
        db.close()
        return jsonify(error_response(error)), 400
    
    # Add comment
    comment, error = TaskService.add_comment(db, task_id, user_id, req.content)
    
    if error:
        db.close()
        return jsonify(error_response(error)), 500
    
    data = comment_to_dict(comment)
    db.close()
    return jsonify(success_response(data)), 201


@tasks_bp.route('/api/workspaces/<int:workspace_id>/tasks/<int:task_id>/comments/<int:comment_id>', methods=['DELETE'])
@require_auth
def delete_comment(user_id, workspace_id, task_id, comment_id):
    """
    Delete comment (comment author or admin only).
    """
    db = get_db()
    
    # Check membership
    is_member = WorkspaceService.is_member(db, user_id, workspace_id)
    if not is_member:
        db.close()
        return jsonify(error_response("Not member of this workspace")), 403
    
    # Verify task is in workspace
    task, error = TaskService.get_task(db, task_id)
    if error or task.workspace_id != workspace_id:
        db.close()
        return jsonify(error_response("Task not found in this workspace")), 404
    
    # Get comment and verify it belongs to task
    from models import TaskComment
    from database import SessionLocal
    comment = db.query(TaskComment).filter(TaskComment.id == comment_id).first()
    if not comment or comment.task_id != task_id:
        db.close()
        return jsonify(error_response("Comment not found")), 404
    
    # Check permission (author or admin)
    is_author = comment.user_id == user_id
    is_admin = WorkspaceService.is_admin(db, user_id, workspace_id)
    
    if not (is_author or is_admin):
        db.close()
        return jsonify(error_response("Permission denied")), 403
    
    # Delete comment
    success, error = TaskService.delete_comment(db, comment_id)
    db.close()
    
    if error:
        return jsonify(error_response(error)), 500
    
    return jsonify(success_response()), 200
