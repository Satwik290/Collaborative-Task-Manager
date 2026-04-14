# Setup & Run Guide

## Prerequisites

- Python 3.9+
- Node.js 16+
- Git

## Quick Start (5 minutes)

### Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Initialize database
python -c "from database import init_db, get_database_url; init_db(get_database_url())"

# Run tests (verify everything works)
pytest -v

# Start server
python app.py
# Server runs on http://localhost:5000
```

### Frontend Setup (in a new terminal)

```bash
cd frontend

# Install dependencies
npm install

# Start development server
npm start
# App runs on http://localhost:3000 (opens automatically)
```

## Using the Application

### Create Test Accounts

**Account 1 (Admin):**
- Email: `admin@example.com`
- Password: `password123`

**Account 2 (Team Member):**
- Email: `member@example.com`
- Password: `password123`

### Demo Flow

1. **Register & Login**
   - Register with admin account
   - Login and see dashboard

2. **Create Workspace**
   - Click "Create a Workspace"
   - Name it: "Q4 Planning"
   - Open the workspace

3. **Create Tasks**
   - Add task: "Design new feature"
   - Add task: "Review PRs"
   - Add task: "Deploy to staging"
   - Update statuses to see changes

4. **Invite Team Member**
   - Click "Invite Member"
   - Invite: `member@example.com` as "member"
   - Verify they appear in team list

5. **Collaborate**
   - Open a task
   - Add comment: "Great idea! Let's discuss this tomorrow"
   - Update task status
   - See comments persist

6. **Login as Team Member**
   - Open new incognito window
   - Login with member account
   - Verify you can see the workspace and tasks
   - Try to delete a task (should be denied)

## Running Tests

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

**Expected results:**
- 46+ tests passing
- 85%+ code coverage
- All permission checks verified

## Stopping Services

```bash
# Backend: Press Ctrl+C
# Frontend: Press Ctrl+C

# Clean up database
rm backend/collab_tasks.db
```

## Troubleshooting

### Backend won't start
```bash
# Make sure port 5000 is free
lsof -i :5000  # Check what's using it
# Or change port in app.py
```

### Frontend shows "Cannot connect to API"
```bash
# Make sure backend is running
# Check REACT_APP_API_URL in frontend/.env
# Verify it's http://localhost:5000
```

### Tests failing
```bash
# Make sure you're in backend/ directory
cd backend

# Check Python version (3.9+)
python --version

# Reinstall dependencies
rm -rf venv
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Run tests again
pytest -v
```

### Database locked
```bash
# SQLite locks during tests - usually temporary
# Restart the application

# Or manually remove database
rm backend/collab_tasks.db
python -c "from database import init_db, get_database_url; init_db(get_database_url())"
```

## Production Notes

For production deployment:

```bash
# Backend
export DATABASE_URL="postgresql://user:pass@host/db"
export JWT_SECRET_KEY="your-random-secret-key-here"
export FLASK_ENV="production"
python app.py

# Frontend
npm run build
# Deploy build/ directory to CDN or static server
# Update REACT_APP_API_URL to production API URL
```

## Documentation

- **README.md** — Full project documentation
- **ARCHITECTURE.md** — System design and decisions
- **SYSTEM_CONSTRAINTS.md** — AI guidance and code rules
- **WALKTHROUGH_SCRIPT.md** — Video presentation guide

## Next Steps

1. ✅ Clone/extract repository
2. ✅ Follow backend setup above
3. ✅ Follow frontend setup above
4. ✅ Run `pytest backend/ -v` to verify tests pass
5. ✅ Follow demo flow above
6. ✅ Record walkthrough video using WALKTHROUGH_SCRIPT.md
7. ✅ Submit to assessments@bettrsw.com

Subject: "Associate Software Engineer - Satwik - Assessment"

---

**Total setup time:** ~5 minutes  
**Demo time:** ~5 minutes  
**Walkthrough video:** 10-15 minutes
