import apiClient from './client';

// Auth
export const auth = {
  register: (email, password) =>
    apiClient.post('/api/auth/register', { email, password }),
  login: (email, password) =>
    apiClient.post('/api/auth/login', { email, password }),
  logout: () =>
    apiClient.post('/api/auth/logout'),
};

// Workspaces
export const workspaces = {
  list: () =>
    apiClient.get('/api/workspaces'),
  create: (name) =>
    apiClient.post('/api/workspaces', { name }),
  get: (id) =>
    apiClient.get(`/api/workspaces/${id}`),
  update: (id, name) =>
    apiClient.put(`/api/workspaces/${id}`, { name }),
  delete: (id) =>
    apiClient.delete(`/api/workspaces/${id}`),
};

// Workspace Members
export const members = {
  list: (workspaceId) =>
    apiClient.get(`/api/workspaces/${workspaceId}/members`),
  invite: (workspaceId, email, role) =>
    apiClient.post(`/api/workspaces/${workspaceId}/members`, { email, role }),
  remove: (workspaceId, userId) =>
    apiClient.delete(`/api/workspaces/${workspaceId}/members/${userId}`),
};

// Tasks
export const tasks = {
  list: (workspaceId) =>
    apiClient.get(`/api/workspaces/${workspaceId}/tasks`),
  create: (workspaceId, title, description, assignedTo) =>
    apiClient.post(`/api/workspaces/${workspaceId}/tasks`, {
      title,
      description,
      assigned_to: assignedTo,
    }),
  get: (workspaceId, taskId) =>
    apiClient.get(`/api/workspaces/${workspaceId}/tasks/${taskId}`),
  update: (workspaceId, taskId, updates) =>
    apiClient.put(`/api/workspaces/${workspaceId}/tasks/${taskId}`, updates),
  delete: (workspaceId, taskId) =>
    apiClient.delete(`/api/workspaces/${workspaceId}/tasks/${taskId}`),
};

// Task Comments
export const comments = {
  list: (workspaceId, taskId) =>
    apiClient.get(`/api/workspaces/${workspaceId}/tasks/${taskId}/comments`),
  add: (workspaceId, taskId, content) =>
    apiClient.post(`/api/workspaces/${workspaceId}/tasks/${taskId}/comments`, {
      content,
    }),
  delete: (workspaceId, taskId, commentId) =>
    apiClient.delete(
      `/api/workspaces/${workspaceId}/tasks/${taskId}/comments/${commentId}`
    ),
};
