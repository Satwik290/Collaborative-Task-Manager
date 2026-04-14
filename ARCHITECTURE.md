# Architecture: Collaborative Task Manager

## Product Vision

A simple task manager where:
- Users create workspaces (teams)
- Users invite others to workspaces
- Users create tasks within workspaces
- Team members can view, comment, and mark tasks complete
- Permissions enforced: only workspace members can access tasks

## Core Models

### User
```
- id (primary key)
- email (unique, required)
- password_hash (required)
- created_at
```

### Workspace
```
- id (primary key)
- name (required)
- created_by (foreign key → User, required)
- created_at
```

### WorkspaceMember
```
- workspace_id (foreign key → Workspace)
- user_id (foreign key → User)
- role ('admin' | 'member')
- joined_at
- PRIMARY KEY: (workspace_id, user_id)
```

### Task
```
- id (primary key)
- workspace_id (foreign key → Workspace, required)
- title (required)
- description (optional)
- status ('todo' | 'in_progress' | 'done')
- assigned_to (foreign key → User, nullable)
- created_by (foreign key → User, required)
- created_at
- updated_at
```

### TaskComment
```
- id (primary key)
- task_id (foreign key → Task, required)
- user_id (foreign key → User, required)
- content (required)
- created_at
```

## API Endpoints

### Auth
```
POST   /api/auth/register          Create user account
POST   /api/auth/login             Login, return JWT
POST   /api/auth/logout            Logout
```

### Workspaces
```
GET    /api/workspaces             List user's workspaces
POST   /api/workspaces             Create workspace
GET    /api/workspaces/:id         Get workspace details
PUT    /api/workspaces/:id         Update workspace (admin only)
DELETE /api/workspaces/:id         Delete workspace (admin only)
```

### Workspace Members
```
GET    /api/workspaces/:id/members       List members
POST   /api/workspaces/:id/members       Invite user (admin only)
DELETE /api/workspaces/:id/members/:uid  Remove member (admin only)
```

### Tasks
```
GET    /api/workspaces/:id/tasks         List tasks in workspace
POST   /api/workspaces/:id/tasks         Create task
GET    /api/workspaces/:id/tasks/:tid    Get task details
PUT    /api/workspaces/:id/tasks/:tid    Update task
DELETE /api/workspaces/:id/tasks/:tid    Delete task
```

### Task Comments
```
GET    /api/workspaces/:id/tasks/:tid/comments      List comments
POST   /api/workspaces/:id/tasks/:tid/comments      Add comment
DELETE /api/workspaces/:id/tasks/:tid/comments/:cid Delete comment
```

## Layer Responsibilities

### API Layer (routes/)
- Validate request structure (schema, types)
- Check authentication (JWT)
- Check authorization (workspace membership, permissions)
- Delegate to business logic
- Return HTTP responses

### Business Logic Layer (services/)
- Enforce business rules (e.g., only admin can remove members)
- Execute workflows (create task with assigned user)
- Validate domain constraints
- Pure functions (no DB access directly)

### Data Layer (models/)
- Define schema with constraints
- Query methods (simple, explicit)
- Never contain business logic

### Models (models/)
- Define domain entities
- SQLAlchemy ORM models
- Constraints at DB level (NOT NULL, UNIQUE, FK)

## Permission Model

### Workspace Access
- Only workspace members can view/modify workspace
- Admin can modify workspace, invite/remove members
- Members can create tasks, comment, update their own assignments

### Task Access
- Only workspace members can view tasks
- Creator can delete their task
- Assigned user can update task status
- Any member can comment

### Enforcement Strategy
- Every route checks: is user member of workspace?
- Every mutation checks: does user have permission?
- Database doesn't grant access implicitly

## Request/Response Patterns

### Success Response
```json
{
  "success": true,
  "data": { ... }
}
```

### Error Response
```json
{
  "success": false,
  "error": "specific error message",
  "details": { ... }  // optional, for validation errors
}
```

### Common HTTP Codes
- 200: OK
- 201: Created
- 400: Validation error
- 401: Not authenticated
- 403: Not authorized
- 404: Not found
- 500: Server error

## Database Constraints

### Enforcement at DB Level
- Foreign key constraints with explicit ON DELETE behavior
- NOT NULL on required fields
- UNIQUE on emails, workspace names per creator
- CHECK constraints on enums (status, role)

### Why Not Just Code-Level Validation?
Database constraints prevent:
- Concurrent write corruption
- Direct DB manipulation breaking invariants
- Accidental data inconsistency

## Change Resilience

### New Feature: "Mark task complete on reaching due date"
**Without resilience:**
- Add due_date field
- Add cron job that updates tasks
- Oops, now users can't see when task auto-completed
- Oops, assigned user gets no notification
- System is fragile

**With resilience (this design):**
1. Add due_date column with migration
2. Write tests: when auto-completed, status changes to 'done'
3. Add task event table to track what changed and when
4. Existing tests still pass (status is still valid)
5. New feature is isolated in cron job
6. Easy to audit: query event table

### Design Decisions Enabling This
- Status as explicit enum (code contracts it)
- Task history optional (can add later)
- Comments unaffected (separate table)
- Auth unchanged (still JWT)

## Observability

### Logging
- All route entry/exit with user ID
- All permission checks
- All database errors
- All validation failures

### Error Messages
- Users see: "You don't have permission to delete this task"
- Logs show: "user_id=5, workspace_id=3, action=delete_task, result=forbidden_not_admin"

## Testing Strategy

### Unit Tests (Business Logic)
- Pure functions, no DB
- Test valid cases, edge cases, error cases

### Integration Tests (Routes + DB)
- Spin up test DB
- Hit routes with auth
- Verify responses and DB state
- Test permission checks explicitly

### Test Coverage Targets
- Routes: 80%+ (all happy paths + auth/permission failures)
- Services: 90%+ (all edge cases)
- Models: 100% (constraints matter)

## Implementation Plan (Priority Order)

1. **Auth** (register, login, JWT)
2. **Workspace CRUD** (create, list, get)
3. **Workspace Members** (invite, list)
4. **Tasks** (create, list, get, update, delete)
5. **Task Comments** (add, list, delete)
6. **Frontend** (React components, forms, state)
7. **Tests** (comprehensive coverage)

Each step builds on previous; tests included at each step.

## Constraints & Trade-offs

### What We're Building
✅ Core collaboration (create, assign, comment)
✅ Permission enforcement
✅ Type safety and validation
✅ Test coverage and resilience

### What We're NOT Building
❌ Real-time notifications (WebSockets)
❌ File attachments
❌ Task templates
❌ Advanced filtering/search
❌ Email notifications
❌ Audit trail (nice to have, not essential)

### Why
- Scope management: core features done really well > many features done okay
- Evaluation criteria focus on quality, not feature count
- 48 hours: time is constrained
- AI assistance is for generating correct, testable code, not building everything

## Tech Stack Rationale

| Choice | Why |
|--------|-----|
| Flask | Simple, explicit, not over-engineered |
| SQLAlchemy | Type hints, clear schema, ORM without magic |
| SQLite (dev) / PostgreSQL (prod) | Relational, strong constraints |
| React | Component model matches UI hierarchy |
| JWT | Stateless auth, simple, no session DB |
| Pytest | Clear test syntax, good fixtures |

## Next Steps

1. Initialize project structure
2. Create database schema and models
3. Implement auth service
4. Implement workspace service
5. Implement task service
6. Build routes for each service
7. Build React frontend
8. Write comprehensive tests
9. Document decisions and risks
10. Record walkthrough

---

**Total Feature Scope:** ~5 hours coding + 2 hours testing + 1 hour docs = manageable in 48 hours with good planning.
