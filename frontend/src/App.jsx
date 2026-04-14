import React, { useState, useEffect } from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider, useAuth } from './context/AuthContext';
import ProtectedRoute from './components/ProtectedRoute';
import LoginPage from './pages/LoginPage';
import RegisterPage from './pages/RegisterPage';
import DashboardPage from './pages/DashboardPage';
import WorkspacePage from './pages/WorkspacePage';
import TaskDetailPage from './pages/TaskDetailPage';
import './index.css';

function Navbar() {
  const { user, isAuth, logout } = useAuth();
  const [theme, setTheme] = useState(localStorage.getItem('theme') || 'light');

  useEffect(() => {
    document.documentElement.setAttribute('data-theme', theme);
    localStorage.setItem('theme', theme);
  }, [theme]);

  const toggleTheme = () => {
    setTheme(prev => prev === 'light' ? 'dark' : 'light');
  };

  if (!isAuth) return null;

  return (
    <nav className="glass" style={{
      padding: '1rem 2rem',
      display: 'flex',
      justifyContent: 'space-between',
      alignItems: 'center',
      borderBottom: '1px solid var(--border-main)',
      position: 'sticky',
      top: 0,
      zIndex: 100
    }}>
      <div style={{ fontWeight: '700', fontSize: '1.25rem', color: 'var(--accent-primary)' }}>
        CollabTasks
      </div>
      <div style={{ display: 'flex', gap: '1rem', alignItems: 'center' }}>
        <button 
          onClick={toggleTheme}
          style={{
            background: 'var(--bg-surface-elevated)',
            padding: '0.5rem 0.75rem',
            borderRadius: 'var(--radius-md)',
            color: 'var(--text-primary)',
            fontSize: '1.2rem',
            border: '1px solid var(--border-main)'
          }}
          title="Toggle Theme"
        >
          {theme === 'light' ? '🌙' : '☀️'}
        </button>
        <span style={{ color: 'var(--text-secondary)', fontSize: '0.9rem' }}>{user?.email}</span>
        <button 
          onClick={logout}
          className="transition-all"
          style={{
            background: 'transparent',
            color: 'var(--accent-danger)',
            fontWeight: '500'
          }}
        >
          Logout
        </button>
      </div>
    </nav>
  );
}

function AppRoutes() {
  const { isAuth, loading } = useAuth();

  if (loading) {
    return <div style={{ padding: '40px', textAlign: 'center' }}>Loading...</div>;
  }

  return (
    <>
      <Navbar />
      <Routes>
        <Route path="/login" element={isAuth ? <Navigate to="/" /> : <LoginPage />} />
        <Route path="/register" element={isAuth ? <Navigate to="/" /> : <RegisterPage />} />
        <Route
          path="/"
          element={
            <ProtectedRoute>
              <DashboardPage />
            </ProtectedRoute>
          }
        />
        <Route
          path="/workspace/:id"
          element={
            <ProtectedRoute>
              <WorkspacePage />
            </ProtectedRoute>
          }
        />
        <Route
          path="/workspace/:workspaceId/task/:taskId"
          element={
            <ProtectedRoute>
              <TaskDetailPage />
            </ProtectedRoute>
          }
        />
        <Route path="*" element={<Navigate to="/" />} />
      </Routes>
    </>
  );
}

export default function App() {
  return (
    <BrowserRouter future={{ v7_startTransition: true, v7_relativeSplatPath: true }}>
      <AuthProvider>
        <AppRoutes />
      </AuthProvider>
    </BrowserRouter>
  );
}
