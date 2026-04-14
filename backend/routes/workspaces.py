"""
Workspace routes.
GET    /api/workspaces
POST   /api/workspaces
GET    /api/workspaces/:id
PUT    /api/workspaces/:id
DELETE /api/workspaces/:id
GET    /api/workspaces/:id/members
POST   /api/workspaces/:id/members
DELETE /api/workspaces/:id/members/:user_id
"""

from flask import Blueprint, request, jsonify
from database import get_db
from auth_middleware import require_auth
from workspace_service import WorkspaceService
from schemas import (
    CreateWorkspaceRequest, UpdateWorkspaceRequest, InviteMemberRequest,
    success_response, error_response, workspace_to_dict, workspace_member_to_dict
)

workspaces_bp = Blueprint('workspaces', __name__, url_prefix='/api/workspaces')


@workspaces_bp.route('', methods=['GET'])
@require_auth
def list_workspaces(user_id):
    """
    List all workspaces user is member of.
    """
    db = get_db()
    workspaces, error = WorkspaceService.get_user_workspaces(db, user_id)
    db.close()
    
    if error:
        return jsonify(error_response(error)), 500
    
    data = [workspace_to_dict(w) for w in workspaces]
    return jsonify(success_response(data)), 200


@workspaces_bp.route('', methods=['POST'])
@require_auth
def create_workspace(user_id):
    """
    Create a new workspace (user becomes admin).
    """
    data = request.get_json(silent=True) or {}
    req, error = CreateWorkspaceRequest.from_json(data)
    if error:
        return jsonify(error_response(error)), 400
    
    db = get_db()
    workspace, error = WorkspaceService.create_workspace(db, user_id, req.name)
    db.close()
    
    if error:
        return jsonify(error_response(error)), 500
    
    return jsonify(success_response(workspace_to_dict(workspace))), 201


@workspaces_bp.route('/<int:workspace_id>', methods=['GET'])
@require_auth
def get_workspace(user_id, workspace_id):
    """
    Get workspace details (user must be member).
    """
    db = get_db()
    
    # Check membership
    is_member = WorkspaceService.is_member(db, user_id, workspace_id)
    if not is_member:
        db.close()
        return jsonify(error_response("Not member of this workspace")), 403
    
    # Get workspace
    workspace, error = WorkspaceService.get_workspace(db, workspace_id)
    db.close()
    
    if error:
        return jsonify(error_response(error)), 404 if "not found" in error.lower() else 500
    
    return jsonify(success_response(workspace_to_dict(workspace))), 200


@workspaces_bp.route('/<int:workspace_id>', methods=['PUT'])
@require_auth
def update_workspace(user_id, workspace_id):
    """
    Update workspace (admin only).
    """
    db = get_db()
    
    # Check admin permission
    is_admin = WorkspaceService.is_admin(db, user_id, workspace_id)
    if not is_admin:
        db.close()
        return jsonify(error_response("Admin permission required")), 403
    
    # Parse request
    data = request.get_json(silent=True) or {}
    req, error = UpdateWorkspaceRequest.from_json(data)
    if error:
        db.close()
        return jsonify(error_response(error)), 400
    
    # Update
    workspace, error = WorkspaceService.update_workspace(db, workspace_id, req.name)
    db.close()
    
    if error:
        return jsonify(error_response(error)), 500
    
    return jsonify(success_response(workspace_to_dict(workspace))), 200


@workspaces_bp.route('/<int:workspace_id>', methods=['DELETE'])
@require_auth
def delete_workspace(user_id, workspace_id):
    """
    Delete workspace (admin only).
    """
    db = get_db()
    
    # Check admin permission
    is_admin = WorkspaceService.is_admin(db, user_id, workspace_id)
    if not is_admin:
        db.close()
        return jsonify(error_response("Admin permission required")), 403
    
    # Delete
    success, error = WorkspaceService.delete_workspace(db, workspace_id)
    db.close()
    
    if error:
        return jsonify(error_response(error)), 500
    
    return jsonify(success_response()), 200


@workspaces_bp.route('/<int:workspace_id>/members', methods=['GET'])
@require_auth
def list_members(user_id, workspace_id):
    """
    List workspace members (user must be member).
    """
    db = get_db()
    
    # Check membership
    is_member = WorkspaceService.is_member(db, user_id, workspace_id)
    if not is_member:
        db.close()
        return jsonify(error_response("Not member of this workspace")), 403
    
    # Get members
    members, error = WorkspaceService.get_members(db, workspace_id)
    
    if error:
        db.close()
        return jsonify(error_response(error)), 500
    
    data = [workspace_member_to_dict(m) for m in members]
    db.close()
    return jsonify(success_response(data)), 200


@workspaces_bp.route('/<int:workspace_id>/members', methods=['POST'])
@require_auth
def invite_member(user_id, workspace_id):
    """
    Invite user to workspace (admin only).
    """
    db = get_db()
    
    # Check admin permission
    is_admin = WorkspaceService.is_admin(db, user_id, workspace_id)
    if not is_admin:
        db.close()
        return jsonify(error_response("Admin permission required")), 403
    
    # Parse request
    data = request.get_json(silent=True) or {}
    req, error = InviteMemberRequest.from_json(data)
    if error:
        db.close()
        return jsonify(error_response(error)), 400
    
    # Add member
    member, error = WorkspaceService.add_member(db, workspace_id, req.email, req.role)
    
    if error:
        db.close()
        return jsonify(error_response(error)), 400
    
    data = workspace_member_to_dict(member)
    db.close()
    return jsonify(success_response(data)), 201


@workspaces_bp.route('/<int:workspace_id>/members/<int:member_user_id>', methods=['DELETE'])
@require_auth
def remove_member(user_id, workspace_id, member_user_id):
    """
    Remove member from workspace (admin only).
    """
    db = get_db()
    
    # Check admin permission
    is_admin = WorkspaceService.is_admin(db, user_id, workspace_id)
    if not is_admin:
        db.close()
        return jsonify(error_response("Admin permission required")), 403
    
    # Remove member
    success, error = WorkspaceService.remove_member(db, workspace_id, member_user_id)
    db.close()
    
    if error:
        return jsonify(error_response(error)), 400
    
    return jsonify(success_response()), 200
