# 🛰️ API Reference: CollabTasks Elite

This guide provides the technical specifications for interacting with the CollabTasks Elite backend.

## 🔑 Authentication
All endpoints (except registration and login) require a **JWT Bearer Token**.

**Header:**
`Authorization: Bearer <your_jwt_token>`

---

## 🔐 Identity & Authentication

### 1. Register Account
`POST /api/auth/register`

- **Payload:**
```json
{
  "email": "user@example.com",
  "password": "securepassword"
}
```
- **Response (201 Created):**
```json
{
  "success": true,
  "data": { "message": "User registered successfully" }
}
```

### 2. Login
`POST /api/auth/login`

- **Payload:**
```json
{
  "email": "user@example.com",
  "password": "securepassword"
}
```
- **Response (200 OK):**
```json
{
  "success": true,
  "data": {
    "token": "eyJhbGci...",
    "user": { "id": 1, "email": "user@example.com" }
  }
}
```

---

## 🏟️ Workspaces (Teams)

### 1. List Workspaces
`GET /api/workspaces`
Returns all workspaces where the current user is a member.

### 2. Create Workspace
`POST /api/workspaces`
- **Payload:** `{ "name": "Project Alpha" }`

### 3. Workspace Details
`GET /api/workspaces/:id`

### 4. Delete Workspace (Admin Only)
`DELETE /api/workspaces/:id`

---

## 👥 Memberships

### 1. List Members
`GET /api/workspaces/:id/members`

### 2. Invite Member (Admin Only)
`POST /api/workspaces/:id/members`
- **Payload:** `{ "email": "colleague@example.com", "role": "member" }`

### 3. Remove Member (Admin Only)
`DELETE /api/workspaces/:id/members/:user_id`

---

## 📋 Tasks (Achievement Units)

### 1. List Tasks
`GET /api/workspaces/:id/tasks`

### 2. Create Task
`POST /api/workspaces/:id/tasks`
- **Payload:**
```json
{
  "title": "Launch Campaign",
  "description": "Finalize the premium branding assets",
  "assigned_to": 5,
  "priority": "high",
  "due_date": "2026-05-01"
}
```

### 3. Update Task
`PUT /api/workspaces/:id/tasks/:task_id`
- **Payload:** `{ "status": "in_progress" }`

### 4. Delete Task (Creator/Admin Only)
`DELETE /api/workspaces/:id/tasks/:task_id`

---

## 💬 Task Comments

### 1. List Comments
`GET /api/workspaces/:id/tasks/:task_id/comments`

### 2. Add Comment
`POST /api/workspaces/:id/tasks/:task_id/comments`
- **Payload:** `{ "content": "Brilliant work on the glassmorphism UI!" }`

### 3. Delete Comment (Author/Admin Only)
`DELETE /api/workspaces/:id/tasks/:task_id/comments/:comment_id`

---

## ⚠️ Error Responses

All errors follow a consistent structure:

```json
{
  "success": false,
  "error": "Unauthorized: Workspace access denied",
  "code": 403
}
```

| Code | Meaning | Outcome |
| :--- | :--- | :--- |
| **400** | Bad Request | Validation failure or malformed JSON. |
| **401** | Unauthorized | Token is missing or invalid. |
| **403** | Forbidden | Insufficient permissions for the resource. |
| **404** | Not Found | Resource does not exist. |
| **500** | Server Error | An internal engine failure occurred. |

---

**Built for Synergy. Documented for Precision.**

---
[Return to README](file:///c:/Users/satwi/Downloads/collab-tasks-assessment/collab-tasks/README.md)
