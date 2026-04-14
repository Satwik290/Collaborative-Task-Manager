# Submission Checklist

Complete this checklist before submitting to assessments@bettrsw.com

## Code Quality ✅

- [ ] All tests passing: `pytest backend/ -v` shows 46+ tests passed
- [ ] Code coverage >80%: `pytest backend/ --cov` 
- [ ] No type errors: All functions have type hints
- [ ] No secret keys in code: Check .gitignore contains venv, __pycache__, .env
- [ ] Clean git history: `git log --oneline` shows meaningful commits

## Backend ✅

- [ ] **models.py** — 5 domain models with constraints (User, Workspace, WorkspaceMember, Task, TaskComment)
- [ ] **auth_service.py** — JWT, password hashing (14 tests passing)
- [ ] **workspace_service.py** — CRUD + permissions (12 tests passing)
- [ ] **task_service.py** — Task + comments (20+ tests passing)
- [ ] **routes/** — Auth, workspaces, tasks (all endpoints implemented)
- [ ] **schemas.py** — Input validation for all requests
- [ ] **tests/** — 46+ tests with <150ms average runtime
- [ ] **requirements.txt** — All dependencies listed
- [ ] **database.py** — SQLite initialization working
- [ ] **conftest.py** — Pytest fixtures configured

**Verification:**
```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python -c "from database import init_db, get_database_url; init_db(get_database_url())"
pytest -v --cov
# Should show: 46+ passed in <10s, 85%+ coverage
```

## Frontend ✅

- [ ] **pages/** — Login, Register, Dashboard, Workspace, TaskDetail
- [ ] **components/** — ProtectedRoute for auth
- [ ] **context/** — AuthContext for state management
- [ ] **api/** — Client and endpoint wrappers
- [ ] **styles/** — Auth.css, Dashboard.css, Workspace.css, TaskDetail.css, index.css
- [ ] **App.jsx** — Routing with protected routes
- [ ] **package.json** — Dependencies: react, axios, react-router-dom
- [ ] **.env** — REACT_APP_API_URL set to http://localhost:5000
- [ ] **public/index.html** — HTML entry point

**Verification:**
```bash
cd frontend
npm install
npm start
# Should open on http://localhost:3000
```

## Documentation ✅

- [ ] **README.md** — 
  - Setup instructions (works in <5 min)
  - Architecture overview with diagram
  - API endpoints list
  - Testing strategy
  - Risks and mitigations
  - Extension strategy
  - Code generation guidelines
  - FAQ section

- [ ] **ARCHITECTURE.md** —
  - Product vision
  - Core models with relationships
  - API endpoints grouped
  - Layer responsibilities
  - Permission model
  - Request/response patterns
  - Database constraints
  - Change resilience examples
  - Technical decision rationale table

- [ ] **SYSTEM_CONSTRAINTS.md** —
  - Core principles (simplicity, defensive, explicit, types, resilience)
  - Code generation rules (DO/DON'T for backend, frontend, database)
  - Architecture rules (boundaries, ownership, forbidden patterns)
  - Testing requirements (coverage targets, test types)
  - AI usage review checklist
  - Risks & mitigations table
  - Extension strategy with examples
  - Questions to ask AI during development

- [ ] **WALKTHROUGH_SCRIPT.md** —
  - Opening (1 min) — Problem & approach
  - Live Demo (3 min) — Register → Dashboard → Workspace → Tasks → Comments
  - Architecture (3 min) — Layer diagram & decisions
  - Code Structure (2 min) — File organization & patterns
  - Testing (2 min) — Test coverage breakdown
  - AI Usage (2 min) — Code review checklist
  - Risks (2 min) — Mitigation strategies
  - Extensions (1 min) — How to add features safely
  - Closing (1 min) — Summary
  - Q&A notes
  - Demo prep checklist
  - Timing breakdown

- [ ] **SETUP_GUIDE.md** —
  - Quick start (5 min)
  - Prerequisites listed
  - Backend setup steps
  - Frontend setup steps
  - Demo flow (6 steps)
  - Running tests
  - Troubleshooting guide
  - Production notes

## GitHub Repository ✅

- [ ] Repository initialized: `git init`
- [ ] All files committed: `git add . && git commit -m "Initial commit"`
- [ ] .gitignore set up correctly
- [ ] No secrets in commits: `grep -r "password\|secret\|key" --include="*.py"` returns only example code
- [ ] Clean history: No merge conflicts or messy commits
- [ ] README visible at repo root

**Verification:**
```bash
git log --oneline          # Shows clean history
git status                 # Should be clean
ls -la                     # Shows README.md, SETUP_GUIDE.md, etc
```

## Walkthrough Video ✅

- [ ] **Duration:** 10-15 minutes
- [ ] **Content includes:**
  - [ ] 1 min — Opening (problem, approach)
  - [ ] 3 min — Live application demo
  - [ ] 3 min — Architecture explanation
  - [ ] 2 min — Code structure walkthrough
  - [ ] 2 min — Testing strategy
  - [ ] 2 min — AI usage & code review
  - [ ] 2 min — Risks & mitigations
  - [ ] 1 min — Extension strategy
  - [ ] 1 min — Closing summary

- [ ] **Recording quality:**
  - [ ] Audio clear and audible
  - [ ] Screen readable (18pt+ font)
  - [ ] Webcam or slide (professional appearance)
  - [ ] Code examples visible (don't read entire files)
  - [ ] Demo smooth (pre-test all interactions)

- [ ] **File format:**
  - [ ] MP4 video (h.264, AAC audio)
  - [ ] <500MB file size
  - [ ] Playable on standard video players

**Recording checklist (use WALKTHROUGH_SCRIPT.md):**
```bash
# Before recording
cd backend && python app.py &
cd frontend && npm start &
pytest backend/ -v  # Shows all tests passing

# During recording
Screen share or present code
Show architecture diagram
Run live demo (register → create workspace → create task → comment)
Show test results
Discuss design decisions
```

## File Structure ✅

```
collab-tasks/
├─ README.md                    ✅ Main documentation
├─ ARCHITECTURE.md              ✅ System design
├─ SYSTEM_CONSTRAINTS.md        ✅ AI guidance
├─ WALKTHROUGH_SCRIPT.md        ✅ Video script
├─ SETUP_GUIDE.md              ✅ Quick start
├─ .gitignore                   ✅ Git config
├─ backend/
│  ├─ models.py                ✅ Domain models
│  ├─ auth_service.py          ✅ Auth logic
│  ├─ workspace_service.py     ✅ Workspace logic
│  ├─ task_service.py          ✅ Task logic
│  ├─ schemas.py               ✅ Validation
│  ├─ auth_middleware.py       ✅ JWT middleware
│  ├─ database.py              ✅ DB connection
│  ├─ app.py                   ✅ Flask app
│  ├─ routes/
│  │  ├─ __init__.py           ✅ Package marker
│  │  ├─ auth.py               ✅ Auth routes
│  │  ├─ workspaces.py         ✅ Workspace routes
│  │  └─ tasks.py              ✅ Task routes
│  ├─ tests/
│  │  ├─ __init__.py           ✅ Package marker
│  │  ├─ test_auth.py          ✅ 14 tests
│  │  ├─ test_workspaces.py    ✅ 12 tests
│  │  └─ test_tasks.py         ✅ 20+ tests
│  ├─ conftest.py              ✅ Pytest config
│  └─ requirements.txt          ✅ Dependencies
└─ frontend/
   ├─ package.json              ✅ NPM config
   ├─ .env                       ✅ API URL
   ├─ public/
   │  └─ index.html             ✅ HTML entry point
   └─ src/
      ├─ index.js               ✅ React entry
      ├─ index.css              ✅ Global styles
      ├─ App.jsx                ✅ Main app
      ├─ api/
      │  ├─ client.js           ✅ Axios client
      │  └─ index.js            ✅ API endpoints
      ├─ context/
      │  └─ AuthContext.jsx     ✅ Auth state
      ├─ components/
      │  └─ ProtectedRoute.jsx  ✅ Route guard
      ├─ pages/
      │  ├─ LoginPage.jsx       ✅ Login
      │  ├─ RegisterPage.jsx    ✅ Register
      │  ├─ DashboardPage.jsx   ✅ Dashboard
      │  ├─ WorkspacePage.jsx   ✅ Workspace
      │  └─ TaskDetailPage.jsx  ✅ Task detail
      └─ styles/
         ├─ Auth.css            ✅ Auth styles
         ├─ Dashboard.css       ✅ Dashboard styles
         ├─ Workspace.css       ✅ Workspace styles
         └─ TaskDetail.css      ✅ Task detail styles
```

## Submission Details ✅

- [ ] **Email:** assessments@bettrsw.com
- [ ] **Subject:** "Associate Software Engineer - Satwik - Assessment"
- [ ] **Email body includes:**
  - [ ] GitHub repository link (or attached zip)
  - [ ] Brief summary of what was built
  - [ ] Key technical decisions (1-2 sentences)
  - [ ] Walkthrough video link (YouTube, Loom, or attachment)
  - [ ] Any special setup notes

**Sample email:**
```
Subject: Associate Software Engineer - Satwik - Assessment

Hi hiring team,

Please find attached my submission for the Associate Software Engineer assessment.

Project: Collaborative Task Manager
- Full-stack application (Flask + React + SQLAlchemy)
- Real-time task management with team collaboration
- Comprehensive test suite (46+ tests, 85%+ coverage)
- Clean architecture with explicit permission checks
- AI-assisted development with strategic code review

Repository: [GitHub link or zip file]

Key technical decisions:
- Layered architecture (API → Service → Data) for testability and maintainability
- JWT authentication for stateless, scalable auth
- Database constraints enforce invariants (no invalid states possible)
- Comprehensive permission checks at every route (not delegated)

Walkthrough video (10-15 min): [Link or attachment]
The video demonstrates the full application flow, architecture, testing strategy, and extension approach.

Please see README.md, SETUP_GUIDE.md, and WALKTHROUGH_SCRIPT.md for full documentation.

Best regards,
Satwik Mohanty
```

## Final Verification ✅

**Before hitting send:**

```bash
# 1. Backend tests pass
cd backend
pytest -v
# Should show: 46+ passed, 0 failed

# 2. Frontend starts
cd frontend
npm install
npm start
# Should open on http://localhost:3000

# 3. Git repo clean
git status
# Should show "nothing to commit, working tree clean"

# 4. All documentation readable
cat README.md
cat ARCHITECTURE.md
cat SYSTEM_CONSTRAINTS.md
# Should all display without errors

# 5. No secrets in code
grep -r "password" backend/ | grep -v test | grep -v example
grep -r "secret" backend/ | grep -v test
# Should return nothing or only example values
```

## Submission Success Checklist ✅

**You're ready to submit when ALL are checked:**

- [ ] **Code:** All tests passing, >80% coverage, no secrets
- [ ] **Backend:** 5 models, 3 services, 3 route files, 3 test files
- [ ] **Frontend:** 5 page components, auth context, API client, 5 CSS files
- [ ] **Documentation:** README, ARCHITECTURE, CONSTRAINTS, SETUP, WALKTHROUGH
- [ ] **Git:** Clean history, no merge conflicts, proper .gitignore
- [ ] **Video:** 10-15 min, covers all required topics, clear audio/video
- [ ] **Email:** Subject correct, content clear, links working

---

**Estimated Timeline:**
- Setup & verification: 30 minutes
- Record walkthrough: 30-45 minutes
- Email & submit: 10 minutes
- **Total: ~90 minutes**

**Deadline:** 48 hours from assessment start

Good luck! 🚀
