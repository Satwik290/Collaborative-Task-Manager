# 🛡️ System Constraints: The Elite Directives

## 🌌 Purpose
This document provides the mathematical and logical boundaries that preserve the integrity of **CollabTasks Elite**. All development, whether by human or AI, must adhere to these laws.

---

## 🏛️ Core Architectural Directives

### 1. The Simplification Law
- **Directive**: Eliminate complexity at the source.
- **Rule**: No decorators, metaclasses, or "magic" abstractions.
- **Outcome**: Code that is immediately understandable, auditable, and resilient.
- **Rationale**: Complexity is the graveyard of security.

### 2. The Defensive Doctrine
- **Directive**: Assume all external data is hostile.
- **Rule**: Validate 100% of inputs at the API boundary using strict Schemas.
- **Constraint**: Database integrity is enforced via `NOT NULL`, `UNIQUE`, `FK`, and `CHECK` constraints.
- **Rationale**: Corruption is prevented, never just "handled."

### 3. The Explicit Identity
- **Directive**: Visibility over transparency.
- **Rule**: All side effects must be visible in function signatures. No implicit auto-joins or cascades.
- **Outcome**: A deterministic system where every action has a clear cause and effect.

### 4. The Layered Sovereignty
- **Directive**: Strict separation of concerns.
- **Boundary 1**: **API** (Validation & Auth).
- **Boundary 2**: **Service** (Domain Logic & Purity).
- **Boundary 3**: **Model** (Schema & Persistence).
- **Law**: Dependencies flow inward. No circular imports. No service logic in routes.

---

## 🎨 Visual & UX Standards (God-Level UI)

For CollabTasks Elite, aesthetics are a functional requirement.

### 1. The Glassmorphism Standard
- **Required**: Use `backdrop-filter: blur()` and semi-transparent backgrounds for primary containers.
- **Required**: Subtle borders (1px solid rgba) to define depth.

### 2. The Dark Mode Orchestration
- **Palette**: Use curated dark HSL values. Avoid `#000` (pure black) unless for deep shadows.
- **Contrast**: Maintain WCAG AA standards while preserving the "Calm Tech" vibe.

### 3. The Motion Law
- **Directive**: Interaction must feel alive.
- **Rule**: Every user action (hover, click, state change) must have a micro-animation (e.g., scale(1.02), opacity shift).
- **Timing**: Use `cubic-bezier` for professional, non-linear easing.

---

## 🧪 Testing & Integrity Mandates

### 1. Proactive Verification
- Every new feature MUST have a corresponding test suite BEFORE being merged.
- **Happy Path**: Verifies achievement.
- **Sad Path**: Verifies rejection of invalidity.
- **Guard Path**: Verifies permission enforcement.

### 2. Coverage Minimums
- **Routes**: 85%+
- **Services**: 95%+
- **Models**: 100%

---

## 🤖 AI Collaboration Guardrails

When generating code for this system, the AI must:
- [ ] Use explicit type hints for ALL function arguments and return types.
- [ ] Ensure every database migration includes appropriate constraints.
- [ ] Verify permission checks are visible and correct in the route logic.
- [ ] Utilize the Design System's defined color tokens and utility classes.
- [ ] **NEVER** skip error handling for "convenience."

---

## ⚔️ Risk & Mitigation Matrix

| Potential Fracture | Defensive Layer | Mitigation Outcome |
| :--- | :--- | :--- |
| **Input Injection** | Strict Schema Validation | Rejection at Boundary |
| **State Corruption** | DB Constraints / Transactions | Atomic Consistency |
| **Logic Regression** | Automated PyTest Suite | Immediate Failure Visibility |
| **Visual Decay** | Design System Constraint Enforcement | Premium Continuity |

---

**Follow these laws to preserve excellence. Violate them and introduce entropy.**

---
[Return to README](file:///c:/Users/satwi/Downloads/collab-tasks-assessment/collab-tasks/README.md)
