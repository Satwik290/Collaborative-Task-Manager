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
      <div className="task-header">
        <button onClick={() => navigate(`/workspace/${workspaceId}`)} className="back-btn">
          ← Back
        </button>
        <h1>{task?.title}</h1>
      </div>

      <div className="task-content">
        {error && <div className="error-message">{error}</div>}

        <div className="task-main">
          <div className="task-details">
            <div className="detail-group">
              <label>Status</label>
              <div className="status-controls">
                {['todo', 'in_progress', 'done'].map((status) => (
                  <button
                    key={status}
                    onClick={() => handleUpdateStatus(status)}
                    disabled={updatingStatus === status}
                    className={`status-btn ${task?.status === status ? 'active' : ''}`}
                  >
                    {status === 'todo' ? 'To Do' : status === 'in_progress' ? 'In Progress' : 'Done'}
                  </button>
                ))}
              </div>
            </div>

            {task?.description && (
              <div className="detail-group">
                <label>Description</label>
                <p>{task.description}</p>
              </div>
            )}

            <div className="detail-group">
              <label>Created</label>
              <p>{new Date(task?.created_at).toLocaleString()}</p>
            </div>
          </div>

          <div className="task-comments">
            <h3>Comments ({commentList.length})</h3>

            <form onSubmit={handleAddComment} className="comment-form">
              <textarea
                value={newComment}
                onChange={(e) => setNewComment(e.target.value)}
                placeholder="Add a comment..."
                rows="3"
              />
              <button type="submit">Comment</button>
            </form>

            {commentList.length === 0 ? (
              <p className="empty-message">No comments yet.</p>
            ) : (
              <div className="comments-list">
                {commentList.map((comment) => (
                  <div key={comment.id} className="comment-item">
                    <div className="comment-header">
                      <span className="comment-author">{comment.email}</span>
                      <span className="comment-date">
                        {new Date(comment.created_at).toLocaleString()}
                      </span>
                    </div>
                    <p>{comment.content}</p>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>

        <button onClick={handleDeleteTask} className="delete-btn">
          Delete Task
        </button>
      </div>
    </div>
  );
}
