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
  const [filterStatus, setFilterStatus] = useState('all');
  const [sortBy, setSortBy] = useState('created_at');
  const [viewMode, setViewMode] = useState('list'); // 'list' or 'calendar'

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
      if (tasksResp.data.success) {
        setTaskList(tasksResp.data.data || []);
      }
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

  const filteredTasks = taskList
    .filter(t => filterStatus === 'all' || t.status === filterStatus)
    .sort((a, b) => {
      if (sortBy === 'priority') {
        const pMap = { high: 0, medium: 1, low: 2 };
        return pMap[a.priority] - pMap[b.priority];
      }
      if (sortBy === 'due_date') {
        if (!a.due_date) return 1;
        if (!b.due_date) return -1;
        return new Date(a.due_date) - new Date(b.due_date);
      }
      return new Date(b.created_at) - new Date(a.created_at);
    });

  const getPriorityColor = (p) => {
    switch(p) {
      case 'high': return 'var(--accent-danger)';
      case 'medium': return 'var(--accent-warning)';
      case 'low': return 'var(--accent-success)';
      default: return 'var(--text-muted)';
    }
  };

  if (loading) return <div className="workspace-page"><p>Loading...</p></div>;

  return (
    <div className="workspace-page">
      <div className="workspace-header">
        <button onClick={() => navigate('/')} className="back-btn transition-all">
          ← Dashboard
        </button>
        <h1>{workspace?.name || 'Workspace'}</h1>
        <div className="view-toggle glass" style={{ borderRadius: 'var(--radius-md)', padding: '4px' }}>
          <button 
            onClick={() => setViewMode('list')}
            style={{ 
              background: viewMode === 'list' ? 'var(--accent-primary)' : 'transparent',
              color: viewMode === 'list' ? 'white' : 'var(--text-primary)',
              padding: '6px 12px',
              borderRadius: 'var(--radius-sm)'
            }}
          >List</button>
          <button 
            onClick={() => setViewMode('calendar')}
            style={{ 
              background: viewMode === 'calendar' ? 'var(--accent-primary)' : 'transparent',
              color: viewMode === 'calendar' ? 'white' : 'var(--text-primary)',
              padding: '6px 12px',
              borderRadius: 'var(--radius-sm)'
            }}
          >Calendar</button>
        </div>
      </div>

      <div className="workspace-grid">
        <div className="tasks-section glass">
          <div className="tasks-controls">
            <h2>
              <span>📋</span> Tasks
            </h2>
            <div className="filters">
              <select value={filterStatus} onChange={(e) => setFilterStatus(e.target.value)}>
                <option value="all">All Status</option>
                <option value="todo">To Do</option>
                <option value="in_progress">In Progress</option>
                <option value="done">Done</option>
              </select>
              <select value={sortBy} onChange={(e) => setSortBy(e.target.value)}>
                <option value="created_at">Newest First</option>
                <option value="priority">Priority</option>
                <option value="due_date">Due Date</option>
              </select>
            </div>
          </div>

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
          ) : viewMode === 'calendar' ? (
             <CalendarView tasks={taskList} onTaskClick={(tid) => navigate(`/workspace/${id}/task/${tid}`)} />
          ) : (
            <div className="tasks-list">
              {filteredTasks.map((task) => (
                <div key={task.id} className={`task-item glass-card status-${task.status}`}>
                  <div className="task-header">
                    <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                      <span className="priority-dot" style={{ 
                        width: '10px', height: '10px', borderRadius: '50%',
                        backgroundColor: getPriorityColor(task.priority)
                      }}></span>
                      <h4>{task.title}</h4>
                    </div>
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
                  
                  <div className="task-meta" style={{ display: 'flex', justifyContent: 'space-between', marginTop: '8px', fontSize: '0.85rem' }}>
                    <span style={{ color: 'var(--text-muted)' }}>
                      {task.due_date ? `📅 ${new Date(task.due_date).toLocaleDateString()}` : 'No due date'}
                    </span>
                    <span style={{ 
                      color: getPriorityColor(task.priority),
                      textTransform: 'capitalize',
                      fontWeight: '600'
                    }}>
                      {task.priority}
                    </span>
                  </div>

                  <button
                    onClick={() =>
                      navigate(`/workspace/${id}/task/${task.id}`)
                    }
                    className="view-task-btn transition-all"
                    style={{ marginTop: '12px' }}
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

function CalendarView({ tasks, onTaskClick }) {
  const [currentDate, setCurrentDate] = useState(new Date());
  
  const daysInMonth = new Date(currentDate.getFullYear(), currentDate.getMonth() + 1, 0).getDate();
  const firstDayOfMonth = new Date(currentDate.getFullYear(), currentDate.getMonth(), 1).getDay();
  
  const days = [];
  for (let i = 0; i < firstDayOfMonth; i++) days.push(null);
  for (let i = 1; i <= daysInMonth; i++) days.push(i);
  
  const nextMonth = () => setCurrentDate(new Date(currentDate.getFullYear(), currentDate.getMonth() + 1));
  const prevMonth = () => setCurrentDate(new Date(currentDate.getFullYear(), currentDate.getMonth() - 1));
  
  const getTasksForDay = (day) => {
    if (!day) return [];
    return tasks.filter(t => {
      if (!t.due_date) return false;
      const d = new Date(t.due_date);
      return d.getDate() === day && 
             d.getMonth() === currentDate.getMonth() && 
             d.getFullYear() === currentDate.getFullYear();
    });
  };

  return (
    <div className="calendar-view glass-card" style={{ padding: '20px' }}>
      <div className="calendar-header" style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '20px' }}>
        <h3>{currentDate.toLocaleString('default', { month: 'long', year: 'numeric' })}</h3>
        <div style={{ display: 'flex', gap: '8px' }}>
          <button onClick={prevMonth} className="back-btn" style={{ padding: '4px 12px' }}>←</button>
          <button onClick={nextMonth} className="back-btn" style={{ padding: '4px 12px' }}>→</button>
        </div>
      </div>
      <div className="calendar-grid" style={{ 
        display: 'grid', 
        gridTemplateColumns: 'repeat(7, 1fr)',
        gap: '8px'
      }}>
        {['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'].map(d => (
          <div key={d} style={{ textAlign: 'center', fontWeight: 'bold', fontSize: '0.8rem', color: 'var(--text-muted)' }}>{d}</div>
        ))}
        {days.map((day, i) => (
          <div key={i} className="calendar-day" style={{ 
            minHeight: '80px', 
            background: day ? 'var(--bg-surface-elevated)' : 'transparent',
            borderRadius: 'var(--radius-md)',
            padding: '4px',
            border: day ? '1px solid var(--border-main)' : 'none'
          }}>
            <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', marginBottom: '4px' }}>{day}</div>
            {getTasksForDay(day).map(task => (
              <div 
                key={task.id} 
                onClick={() => onTaskClick(task.id)}
                style={{
                  fontSize: '0.7rem',
                  padding: '2px 4px',
                  background: 'var(--accent-primary)',
                  color: 'white',
                  borderRadius: '4px',
                  marginBottom: '2px',
                  cursor: 'pointer',
                  whiteSpace: 'nowrap',
                  overflow: 'hidden',
                  textOverflow: 'ellipsis'
                }}
                title={task.title}
              >
                {task.title}
              </div>
            ))}
          </div>
        ))}
      </div>
    </div>
  );
}
