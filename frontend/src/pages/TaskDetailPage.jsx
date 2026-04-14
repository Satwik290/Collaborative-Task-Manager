import React, { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { tasks, comments } from '../api';
import '../styles/TaskDetail.css';

export default function TaskDetailPage() {
  const { workspaceId, taskId } = useParams();
  const navigate = useNavigate();
  const [task, setTask] = useState(null);
  const [commentList, setCommentList] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [newComment, setNewComment] = useState('');
  const [updatingStatus, setUpdatingStatus] = useState(null);

  useEffect(() => {
    fetchTaskData();
  }, [taskId]);

  const fetchTaskData = async () => {
    try {
      setLoading(true);
      const taskResp = await tasks.get(workspaceId, taskId);
      const commentsResp = await comments.list(workspaceId, taskId);

      if (taskResp.data.success) setTask(taskResp.data.data);
      if (commentsResp.data.success) setCommentList(commentsResp.data.data || []);
    } catch (err) {
      setError(err.response?.data?.error || 'Failed to load task');
    } finally {
      setLoading(false);
    }
  };

  const handleAddComment = async (e) => {
    e.preventDefault();
    if (!newComment.trim()) return;

    try {
      const response = await comments.add(workspaceId, taskId, newComment);
      if (response.data.success) {
        setNewComment('');
        fetchTaskData();
      }
    } catch (err) {
      setError(err.response?.data?.error || 'Failed to add comment');
    }
  };

  const handleUpdateStatus = async (newStatus) => {
    setUpdatingStatus(newStatus);
    try {
      const response = await tasks.update(workspaceId, taskId, {
        status: newStatus,
      });
      if (response.data.success) {
        setTask({ ...task, status: newStatus });
      }
    } catch (err) {
      setError(err.response?.data?.error || 'Failed to update task');
    } finally {
      setUpdatingStatus(null);
    }
  };

  const handleDeleteTask = async () => {
    if (!window.confirm('Are you sure? This cannot be undone.')) return;

    try {
      await tasks.delete(workspaceId, taskId);
      navigate(`/workspace/${workspaceId}`);
    } catch (err) {
      setError(err.response?.data?.error || 'Failed to delete task');
    }
  };

  if (loading) return <div className="task-detail-page"><p>Loading...</p></div>;

  return (
    <div className="task-detail-page">
      <div className="task-detail-container glass-card">
        <div className="task-detail-header">
          <button onClick={() => navigate(`/workspace/${workspaceId}`)} className="back-btn transition-all">
            ← Back to Workspace
          </button>
          <h1>{task?.title}</h1>
          {error && <div className="error-message" style={{ marginTop: '1rem' }}>{error}</div>}
        </div>

        <div className="task-info-grid">
          <div className="info-item">
            <label>Current Status</label>
            <p style={{ textTransform: 'capitalize', color: `var(--accent-${task?.status === 'done' ? 'success' : task?.status === 'in_progress' ? 'warning' : 'primary'})` }}>
              {task?.status?.replace('_', ' ')}
            </p>
          </div>
          <div className="info-item">
            <label>Timeline</label>
            <p>{new Date(task?.created_at).toLocaleDateString()}</p>
          </div>
          <div className="info-item">
            <label>Actions</label>
            <select
              className="transition-all"
              value={task?.status}
              onChange={(e) => handleUpdateStatus(e.target.value)}
              disabled={updatingStatus}
            >
              <option value="todo">To Do</option>
              <option value="in_progress">In Progress</option>
              <option value="done">Done</option>
            </select>
          </div>
        </div>

        <div className="description-section">
          <h3>Description</h3>
          <div className="description-box glass">
            {task?.description || <span style={{ color: 'var(--text-muted)' }}>No description provided for this task.</span>}
          </div>
        </div>

        <div className="comments-section">
          <h3>Discussion ({commentList.length})</h3>

          <form onSubmit={handleAddComment} className="comment-form">
            <textarea
              className="transition-all"
              value={newComment}
              onChange={(e) => setNewComment(e.target.value)}
              placeholder="Write a message..."
              rows="3"
            />
            <button type="submit" className="transition-all">Post Comment</button>
          </form>

          {commentList.length === 0 ? (
            <p className="empty-message glass" style={{ borderStyle: 'solid', padding: '2rem' }}>
              No comments yet. Start the conversation!
            </p>
          ) : (
            <div className="comments-list">
              {commentList.map((comment) => (
                <div key={comment.id} className="comment-item glass transition-all">
                  <div className="comment-meta">
                    <span className="comment-author">{comment.email}</span>
                    <span className="comment-date">
                      {new Date(comment.created_at).toLocaleDateString()}
                    </span>
                  </div>
                  <div className="comment-content">{comment.content}</div>
                </div>
              ))}
            </div>
          )}
        </div>

        <div style={{ marginTop: '4rem', paddingTop: '2rem', borderTop: '1px solid var(--border-subtle)' }}>
          <button onClick={handleDeleteTask} className="logout-btn transition-all" style={{ padding: '0.75rem 1.5rem' }}>
            Delete Permanently
          </button>
        </div>
      </div>
    </div>
  );
}
