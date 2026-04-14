# System Constraints & AI Guidance

## Purpose
This document constrains AI behavior and protects system integrity during development. All generated code must be reviewed against these rules.

---

## Core Principles

### 1. Simplicity Over Cleverness
- ❌ Complex patterns, decorators, metaclasses
- ✅ Straightforward conditionals, loops, explicit calls
- ✅ Code that reads like the problem domain
- Rationale: Collaborative todo apps are inherently simple; complexity hides bugs

### 2. Defensive by Default
- All user inputs validated at API boundary (not trusted)
- Database constraints enforced (unique, NOT NULL, foreign keys)
- Invalid state prevention > error handling
- Validation errors returned clearly to client
- Rationale: Prevent corruption before it happens

### 3. Explicit Over Implicit
- No magic (no ORM auto-joins, no implicit cascades)
- SQL queries written explicitly or via ORM with explicit load strategy
- All side effects visible in function signatures
- Rationale: Easy to audit and extend

### 4. Types & Schemas as Guards
- Python: Use type hints on every function
- Database: Proper schemas with constraints
- API: Request/response schemas validated
- Rationale: Catch mistakes at compile/validation time

### 5. Change Resilience
- Decisions made at layers (don't scatter permissions logic everywhere)
- Dependencies flow one direction (never circular)
- Tests prove new code doesn't break old behavior
- Rationale: New features shouldn't ripple through codebase

---

## Code Generation Rules (for AI)

### Backend (Flask + Python)

**DO:**
- Generate boilerplate (models, schemas, routes) with type hints
- Use SQLAlchemy ORM for schema definition and basic queries
- Validate ALL inputs with clear error messages
- Write explicit SQL for complex queries
- Use descriptive variable names matching domain language
- Include docstrings explaining non-obvious logic
- Generate test cases that prove correctness

**DON'T:**
- Use decorators/metaclasses for logic (use explicit functions)
- Generate implicit behavior (auto-cascade deletes, hidden side effects)
- Assume user input is safe
- Write clever one-liners (clarity > brevity)
- Generate routes without validating request structure
- Skip error handling for invalid states

### Frontend (React)

**DO:**
- Generate component hierarchy matching data structure
- Use React hooks (useState, useContext) explicitly
- Validate form inputs before submission
- Show clear error states and user feedback
- Use prop types or TypeScript for component contracts
- Generate loading/error/success UI states

**DON'T:**
- Generate implicit state management (use explicit context/hooks)
- Trust API responses without validation
- Skip error handling
- Create deeply nested components (break into smaller pieces)

### Database

**DO:**
- Define schemas with constraints (NOT NULL, UNIQUE, FK)
- Use foreign keys with explicit CASCADE/RESTRICT
- Index on foreign keys and frequently filtered columns
- Write migration scripts for schema changes

**DON'T:**
- Store computed values (calculate on read)
- Skip NOT NULL constraints
- Use implicit enum handling (store explicit strings with CHECK constraints)

---

## Architecture Rules

### Boundaries
1. **API Layer** — Validates all inputs, returns HTTP + JSON
2. **Business Logic** — Pure logic, no database access (testable)
3. **Data Layer** — Database access only, no business rules
4. **Models** — Define domain (Task, User, Collaboration)

### Ownership
- Each route owns its validation
- Each model owns its constraints
- Tests own proving correctness

### Forbidden Patterns
- ❌ Database logic in routes
- ❌ Business logic in database queries
- ❌ Validation split across layers
- ❌ Circular dependencies

---

## Testing Requirements

Every feature must have tests proving:
1. Happy path works correctly
2. Invalid inputs are rejected
3. Permissions/auth are enforced
4. New feature doesn't break existing behavior

**Test Coverage Minimum:**
- API routes: 80%+
- Business logic: 90%+
- Database models: 100% (constraints, relationships)

---

## AI Usage Review Checklist

**Before accepting AI-generated code:**
- [ ] Type hints present on all functions
- [ ] Input validation explicit and clear
- [ ] No implicit behavior
- [ ] Database constraints enforced
- [ ] Error paths tested
- [ ] Code reads naturally (not clever)
- [ ] No security vulnerabilities
- [ ] Tests provided and passing

---

## Risks & Mitigations

| Risk | Mitigation |
|------|-----------|
| Scope creep (too many features) | Build core features only; document extensions |
| AI generates untested code | Every generated function must have tests |
| Implicit bugs from AI | Code review + type checking + tests |
| Permissions not enforced | Test every permission check explicitly |
| Database corruption | Constraints prevent invalid states |

---

## Extension Strategy

When adding new features:
1. **Identify the boundary** — Which layer does it touch?
2. **Write tests first** — Prove the behavior before code
3. **Add schema changes** — Migrations with constraints
4. **Implement business logic** — Separate from routes
5. **Add routes** — Validate and delegate to logic
6. **Verify resilience** — Existing tests still pass

This prevents feature sprawl and keeps complexity manageable.

---

## Questions to Ask AI During Development

- "Is this the simplest way to solve this?"
- "What could go wrong with this input?"
- "Does this enforce the constraint at the database level?"
- "Could this change break existing behavior?"
- "Are all error cases tested?"

---

## Evaluation Alignment

These constraints directly support the evaluation criteria:
- **Structure:** Clear boundaries and layering
- **Simplicity:** Explicit code, no magic
- **Correctness:** Validation + constraints prevent invalid states
- **Interface Safety:** Schemas and validation guard APIs
- **Change Resilience:** Tests prove new code doesn't break old
- **Verification:** Automated tests + type hints
- **Observability:** Clear errors, explicit logic
- **AI Guidance:** This document guides all code generation
