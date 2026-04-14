import React, { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { workspaces, tasks, members } from '../api';
import '../styles/Workspace.css';

export default function WorkspacePage() {
  const { id } = useParams();
  const navigate = useNavigate();
  const [workspace, setWorkspace] = useState(null);
  const [taskList, setTaskList] = useState([]);
  const [memberList, setMemberList] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [newTaskTitle, setNewTaskTitle] = useState('');
  const [showInvite, setShowInvite] = useState(false);
  const [inviteEmail, setInviteEmail] = useState('');
  const [inviteRole, setInviteRole] = useState('member');

  useEffect(() => {
    fetchWorkspaceData();
  }, [id]);

  const fetchWorkspaceData = async () => {
    try {
      setLoading(true);
      setError('');

      const wsResp = await workspaces.get(id);
      const tasksResp = await tasks.list(id);
      const membersResp = await members.list(id);

      if (wsResp.data.success) setWorkspace(wsResp.data.data);
      if (tasksResp.data.success) setTaskList(tasksResp.data.data || []);
      if (membersResp.data.success) setMemberList(membersResp.data.data || []);
    } catch (err) {
      setError(err.response?.data?.error || 'Failed to load workspace');
    } finally {
      setLoading(false);
    }
  };

  const handleCreateTask = async (e) => {
    e.preventDefault();
    if (!newTaskTitle.trim()) return;

    try {
      const response = await tasks.create(id, newTaskTitle, '', null);
      if (response.data.success) {
        setNewTaskTitle('');
        fetchWorkspaceData();
      } else {
        setError(response.data.error);
      }
    } catch (err) {
      setError(err.response?.data?.error || 'Failed to create task');
    }
  };

  const handleInviteMember = async (e) => {
    e.preventDefault();
    try {
      const response = await members.invite(id, inviteEmail, inviteRole);
      if (response.data.success) {
        setInviteEmail('');
        setShowInvite(false);
        fetchWorkspaceData();
      } else {
        setError(response.data.error);
      }
    } catch (err) {
      setError(err.response?.data?.error || 'Failed to invite member');
    }
  };

  const handleUpdateTaskStatus = async (taskId, newStatus) => {
    try {
      const response = await tasks.update(id, taskId, { status: newStatus });
      if (response.data.success) {
        setTaskList(
          taskList.map((t) =>
            t.id === taskId ? { ...t, status: newStatus } : t
          )
        );
      }
    } catch (err) {
      setError(err.response?.data?.error || 'Failed to update task');
    }
  };

  if (loading) return <div className="workspace-page"><p>Loading...</p></div>;

  return (
    <div className="workspace-page">
      <div className="workspace-header">
        <button onClick={() => navigate('/')} className="back-btn transition-all">
          ← Back to Dashboard
        </button>
        <h1>{workspace?.name || 'Workspace'}</h1>
        <div style={{ width: '150px' }}></div> {/* Spacer for symmetry */}
      </div>

      <div className="workspace-grid">
        <div className="tasks-section glass">
          <h2>
            <span>📋</span> Tasks
            {error && <span className="error-message" style={{ margin: 0, padding: '2px 8px', fontSize: '12px' }}>{error}</span>}
          </h2>

          <form onSubmit={handleCreateTask} className="create-task-form">
            <input
              type="text"
              value={newTaskTitle}
              className="transition-all"
              onChange={(e) => setNewTaskTitle(e.target.value)}
              placeholder="What needs to be done?"
              required
            />
            <button type="submit" className="transition-all">Add Task</button>
          </form>

          {taskList.length === 0 ? (
            <div className="empty-message">
              <p>No tasks yet. Create your first task above!</p>
            </div>
          ) : (
            <div className="tasks-list">
              {taskList.map((task) => (
                <div key={task.id} className={`task-item glass-card status-${task.status}`}>
                  <div className="task-header">
                    <h4>{task.title}</h4>
                    <select
                      className="transition-all"
                      value={task.status}
                      onChange={(e) =>
                        handleUpdateTaskStatus(task.id, e.target.value)
                      }
                    >
                      <option value="todo">To Do</option>
                      <option value="in_progress">In Progress</option>
                      <option value="done">Done</option>
                    </select>
                  </div>
                  {task.description && <p>{task.description}</p>}
                  
                  <button
                    onClick={() =>
                      navigate(`/workspace/${id}/task/${task.id}`)
                    }
                    className="view-task-btn transition-all"
                  >
                    View Details →
                  </button>
                </div>
              ))}
            </div>
          )}
        </div>

        <div className="team-section glass">
          <h2><span>👥</span> Team</h2>

          <div className="members-list">
            {memberList.map((member) => (
              <div key={member.user_id} className="member-item transition-all">
                <p className="member-email">{member.email}</p>
                <p className="member-role">{member.role}</p>
              </div>
            ))}
          </div>

          {!showInvite ? (
            <button
              onClick={() => setShowInvite(true)}
              className="invite-btn transition-all"
            >
              + Invite Member
            </button>
          ) : (
            <form onSubmit={handleInviteMember} className="invite-form glass-card">
              <input
                type="email"
                value={inviteEmail}
                className="transition-all"
                onChange={(e) => setInviteEmail(e.target.value)}
                placeholder="Member email"
                required
              />
              <select
                className="transition-all"
                value={inviteRole}
                onChange={(e) => setInviteRole(e.target.value)}
              >
                <option value="member">Member</option>
                <option value="admin">Admin</option>
              </select>
              <div className="form-buttons">
                <button type="submit" className="transition-all">Invite</button>
                <button
                  type="button"
                  onClick={() => setShowInvite(false)}
                  className="cancel-btn transition-all"
                >
                  Cancel
                </button>
              </div>
            </form>
          )}
        </div>
      </div>
    </div>
  );
}
