import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { workspaces } from '../api';
import { useAuth } from '../context/AuthContext';
import '../styles/Dashboard.css';

export default function DashboardPage() {
  const [workspaceList, setWorkspaceList] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [newWorkspaceName, setNewWorkspaceName] = useState('');
  const [creating, setCreating] = useState(false);
  const navigate = useNavigate();
  const { logout } = useAuth();

  useEffect(() => {
    fetchWorkspaces();
  }, []);

  const fetchWorkspaces = async () => {
    try {
      setError('');
      const response = await workspaces.list();
      if (response.data.success) {
        setWorkspaceList(response.data.data || []);
      } else {
        setError(response.data.error);
      }
    } catch (err) {
      setError(err.response?.data?.error || 'Failed to load workspaces');
    } finally {
      setLoading(false);
    }
  };

  const handleCreateWorkspace = async (e) => {
    e.preventDefault();
    if (!newWorkspaceName.trim()) return;

    setCreating(true);
    try {
      const response = await workspaces.create(newWorkspaceName);
      if (response.data.success) {
        setNewWorkspaceName('');
        fetchWorkspaces();
      } else {
        setError(response.data.error);
      }
    } catch (err) {
      setError(err.response?.data?.error || 'Failed to create workspace');
    } finally {
      setCreating(false);
    }
  };

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  return (
    <div className="dashboard-page">
      <div className="dashboard-header">
        <h1>TaskCollab</h1>
        <button onClick={handleLogout} className="logout-btn">
          Logout
        </button>
      </div>

      <div className="dashboard-content">
        <div className="create-workspace">
          <h2>Create a Workspace</h2>
          <form onSubmit={handleCreateWorkspace}>
            {error && <div className="error-message">{error}</div>}
            <input
              type="text"
              value={newWorkspaceName}
              onChange={(e) => setNewWorkspaceName(e.target.value)}
              placeholder="Workspace name..."
              required
            />
            <button type="submit" disabled={creating}>
              {creating ? 'Creating...' : 'Create'}
            </button>
          </form>
        </div>

        <div className="workspaces-section">
          <h2>Your Workspaces</h2>
          {loading ? (
            <p>Loading...</p>
          ) : workspaceList.length === 0 ? (
            <p className="empty-message">No workspaces yet. Create one above!</p>
          ) : (
            <div className="workspaces-grid">
              {workspaceList.map((ws) => (
                <div
                  key={ws.id}
                  className="workspace-card"
                  onClick={() => navigate(`/workspace/${ws.id}`)}
                >
                  <h3>{ws.name}</h3>
                  <p>{new Date(ws.created_at).toLocaleDateString()}</p>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
