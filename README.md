# Collaborative Task Manager

A simple, well-structured task management application with real-time collaboration features. Built with Flask, React, and SQLAlchemy to demonstrate clean architecture, defensive programming, and AI-assisted development.

## Quick Start

### Backend Setup (Python 3.9+)

```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

pip install -r requirements.txt

# Initialize database
python -c "from database import init_db, get_database_url; init_db(get_database_url())"

# Run tests
pytest -v --cov

# Start server
python app.py
# Server runs on http://localhost:5000
```

### Frontend Setup (Node 16+)

```bash
cd frontend
npm install
npm start
# App runs on http://localhost:3000
```

## Architecture Overview

### Core Design Principles

**1. Simplicity Over Cleverness**
- Explicit code that reads like the problem domain
- No decorators, metaclasses, or hidden behavior
- Straightforward conditionals and loops

**2. Defensive by Default**
- All inputs validated at API boundary
- Database constraints enforce invariants
- Invalid states prevented, not handled after the fact

**3. Clear Boundaries**
- **API Layer** (routes/) — Validates input, checks auth/permissions, delegates to services
- **Business Logic** (services/) — Pure functions, domain rules, testable in isolation
- **Data Layer** (models/) — Schema definition, constraints, simple queries
- **Database** — SQLite (dev) / PostgreSQL (prod)

**4. Permission Enforcement**
- Every route checks: "Is user member of workspace?"
- Every mutation checks: "Does user have permission?"
- Permission checks explicit and testable

### Data Model

```
User
├─ email (unique)
├─ password_hash
└─ created_at

Workspace
├─ name
├─ created_by (→ User)
├─ created_at
└─ members (WorkspaceMember[])
   └─ tasks (Task[])

WorkspaceMember
├─ workspace_id (FK)
├─ user_id (FK)
├─ role ('admin' | 'member')
└─ joined_at

Task
├─ workspace_id (FK)
├─ title
├─ description
├─ status ('todo' | 'in_progress' | 'done')
├─ assigned_to (→ User, nullable)
├─ created_by (→ User)
├─ created_at
├─ updated_at
└─ comments (TaskComment[])

TaskComment
├─ task_id (FK)
├─ user_id (FK)
├─ content
└─ created_at
```

### Key Technical Decisions

| Decision | Why |
|----------|-----|
| **SQLAlchemy ORM** | Type hints, explicit schema, constraints at DB level |
| **JWT Authentication** | Stateless, simple, no session storage |
| **Explicit Permission Checks** | Every route enforces, not delegated to middleware |
| **DB Constraints** | CHECK, UNIQUE, NOT NULL prevent corruption |
| **Separate Services** | Business logic testable without Flask/HTTP |
| **Request Validation Schemas** | All inputs validated at boundary |
| **Response Consistency** | All endpoints return {success, data/error} |

### API Endpoints

#### Authentication
```
POST   /api/auth/register      Create user account
POST   /api/auth/login         Authenticate, return JWT
POST   /api/auth/logout        Logout (stateless)
```

#### Workspaces
```
GET    /api/workspaces              List user's workspaces
POST   /api/workspaces              Create workspace
GET    /api/workspaces/:id          Get workspace details
PUT    /api/workspaces/:id          Update (admin only)
DELETE /api/workspaces/:id          Delete (admin only)
```

#### Workspace Members
```
GET    /api/workspaces/:id/members         List members
POST   /api/workspaces/:id/members         Invite user (admin only)
DELETE /api/workspaces/:id/members/:uid    Remove member (admin only)
```

#### Tasks
```
GET    /api/workspaces/:id/tasks                List tasks
POST   /api/workspaces/:id/tasks                Create task
GET    /api/workspaces/:id/tasks/:task_id       Get task
PUT    /api/workspaces/:id/tasks/:task_id       Update task
DELETE /api/workspaces/:id/tasks/:task_id       Delete (creator/admin only)
```

#### Task Comments
```
GET    /api/workspaces/:id/tasks/:task_id/comments       List comments
POST   /api/workspaces/:id/tasks/:task_id/comments       Add comment
DELETE /api/workspaces/:id/tasks/:task_id/comments/:cid  Delete (author/admin only)
```

## Testing Strategy

### Test Coverage
- **Auth**: 14 tests (password hashing, token generation, registration, login)
- **Workspaces**: 12 tests (CRUD, membership, permissions)
- **Tasks**: 20+ tests (CRUD, comments, assignments, permissions)

### Running Tests
```bash
# All tests
pytest backend/ -v

# With coverage
pytest backend/ --cov=. --cov-report=html

# Specific test file
pytest backend/tests/test_auth.py -v

# Specific test
pytest backend/tests/test_auth.py::TestAuthService::test_hash_password -v
```

### Test Design Principles
- **Isolation**: In-memory SQLite for each test
- **Clarity**: Test names describe exactly what's being tested
- **Completeness**: Happy path + error cases + permissions
- **Resilience**: New tests don't break existing tests

## Risks & Mitigations

| Risk | Impact | Mitigation |
|------|--------|-----------|
| **Scope creep** | Feature bloat, unmaintainable | Build core features only; document extensions |
| **AI-generated bugs** | Untested code in production | Every generated function has tests |
| **Permission bypass** | Unauthorized access | Every route explicitly checks; tests verify |
| **Database corruption** | Invalid states | Constraints prevent at DB level |
| **Concurrent writes** | Race conditions | DB transactions, constraints |

## Extension Strategy

### How to Add a Feature Safely

1. **Identify the boundary** — Which layer? (API/Service/Data)
2. **Write tests first** — Prove desired behavior before code
3. **Add schema changes** — Migration + constraints
4. **Implement logic** — Service layer, pure function
5. **Add routes** — Validate, check perms, delegate
6. **Verify resilience** — Run all tests, check coverage

### Example: "Recurring Tasks"

```
1. Add schema:
   - task.recurrence_pattern (null, "daily", "weekly", "monthly")
   - task.next_due_date (nullable)

2. Write tests:
   - test_create_recurring_task
   - test_recurring_tasks_dont_break_existing_tests
   - test_recurring_task_permission_checks

3. Add service method:
   - TaskService.create_recurring_task()
   - Return regular Task (decompose in API)

4. Add route:
   - POST /api/workspaces/:id/tasks with recurrence_pattern
   - Existing tests still pass

5. Add cron job:
   - Query tasks with recurrence + due date
   - Clone to new task (original stays for history)
```

Key: Original code unchanged, new code isolated, tests prove safety.

## Code Generation Guidelines

This project uses AI assistance with explicit constraints. See `SYSTEM_CONSTRAINTS.md` for:
- What code should/shouldn't do
- Validation and constraint rules
- Testing requirements
- Code review checklist before accepting generated code

### Code Review Before Accepting Generated Code

- [ ] Type hints present on all functions
- [ ] Input validation explicit and clear
- [ ] No implicit behavior (no magic)
- [ ] Database constraints enforced
- [ ] Error paths tested
- [ ] Code reads naturally (not clever)
- [ ] No security vulnerabilities
- [ ] Tests provided and passing

## Observability

### Logging
- Routes log entry/exit with user ID
- Permission checks logged
- Database errors logged
- Validation failures logged

### Error Messages
- User-facing: Clear, actionable (e.g., "You don't have permission to delete this task")
- Logs: Detailed context (user_id, workspace_id, action, result)

## Development Workflow

### Adding a new feature

1. Read `SYSTEM_CONSTRAINTS.md` — Understand constraints
2. Read `ARCHITECTURE.md` — Understand how features fit
3. Write tests first — Describe the behavior
4. Implement service — Pure business logic
5. Add routes — Validate and delegate
6. Run full test suite — `pytest backend/ -v`
7. Verify coverage — `pytest --cov`

### Making a commit

```bash
# All tests passing
pytest backend/ -v

# No regressions
pytest backend/ --cov

# Clean code
# (no type errors, proper structure)

# Commit with clear message
git commit -m "Add task assignment feature

- Add assigned_to field to Task model
- Add permission check: only admin can assign
- Add tests for happy path and permission denial
- No existing tests broken"
```

## FAQ

**Q: Why no real-time updates?**
A: Scope management. Real-time sync (WebSockets) adds significant complexity. Core feature (task management) done well > many half-baked features.

**Q: Why SQLite for dev, PostgreSQL for prod?**
A: SQLite great for local development (no setup), PostgreSQL for production (concurrent writes, advanced constraints).

**Q: Why JWT tokens instead of sessions?**
A: Stateless (no session DB), simple to test, scales across services.

**Q: Can I add file attachments?**
A: Yes. Add schema (Attachment table), routes, validation. Tests should verify permission checks. See extension strategy.

**Q: How do I know the code is correct?**
A: Tests. Every feature has tests proving happy path + error cases. Run `pytest --cov` to see coverage.

## Deployment

### Local Development
```bash
# Terminal 1: Backend
cd backend && python app.py

# Terminal 2: Frontend
cd frontend && npm start
```

### Production
```bash
# Backend
export DATABASE_URL="postgresql://user:pass@host/db"
export JWT_SECRET_KEY="your-secret-key"
export FLASK_ENV="production"
python app.py

# Frontend
npm run build
# Deploy build/ directory to CDN or static server
```

## Troubleshooting

### Tests failing
```bash
# Check database is clean
rm collab_tasks.db

# Run specific test
pytest backend/tests/test_auth.py::TestAuthService::test_hash_password -v

# Check for type errors
# (Review code in models.py, services, routes)
```

### API returns 401 Unauthorized
- Token missing? Check Authorization header: `Authorization: Bearer <token>`
- Token expired? Get new token from /api/auth/login
- Invalid token? Verify JWT_SECRET_KEY matches

### API returns 403 Forbidden
- Not workspace member? Use /api/workspaces/:id/members to invite user
- Not admin? Only admins can delete workspaces, invite members
- Not creator? Only task creator or admin can delete task

## Project Structure

```
collab-tasks/
├─ backend/
│  ├─ models.py           Domain models with DB constraints
│  ├─ auth_service.py     Auth business logic
│  ├─ workspace_service.py Workspace business logic
│  ├─ task_service.py     Task business logic
│  ├─ schemas.py          Request/response validation
│  ├─ auth_middleware.py  JWT verification
│  ├─ app.py              Flask app factory
│  ├─ database.py         DB connection
│  ├─ routes/
│  │  ├─ auth.py          Auth routes
│  │  ├─ workspaces.py    Workspace routes
│  │  └─ tasks.py         Task routes
│  ├─ tests/
│  │  ├─ test_auth.py
│  │  ├─ test_workspaces.py
│  │  └─ test_tasks.py
│  ├─ requirements.txt
│  └─ conftest.py         Pytest fixtures
├─ frontend/
│  ├─ src/
│  │  ├─ App.jsx
│  │  ├─ pages/
│  │  ├─ components/
│  │  ├─ api/
│  │  └─ context/
│  ├─ package.json
│  └─ .env                API URL config
├─ SYSTEM_CONSTRAINTS.md  AI guidance + code rules
├─ ARCHITECTURE.md        System design
└─ README.md             This file
```

## References

- **SQLAlchemy Docs**: https://docs.sqlalchemy.org
- **Flask Docs**: https://flask.palletsprojects.com
- **JWT Spec**: https://tools.ietf.org/html/rfc7519
- **React Hooks**: https://react.dev/reference/react

---

**Built with AI assistance, reviewed for correctness and safety.**
