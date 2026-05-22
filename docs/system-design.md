# System Design Document
## CodeMentor — AI-Powered Code Review for Beginner Programmers

**Version:** 1.0  
**Author:** Nour Zahrawi  
**Date:** May 2026  
**Status:** Approved

---

## Table of Contents

1. [System Overview](#1-system-overview)
2. [Architecture](#2-architecture)
3. [Technology Decisions](#3-technology-decisions)
4. [Component Design](#4-component-design)
5. [Data Flow](#5-data-flow)
6. [Database Schema](#6-database-schema)
7. [API Design](#7-api-design)
8. [Prompt Engineering Strategy](#8-prompt-engineering-strategy)
9. [Security Design](#9-security-design)
10. [Deployment Architecture](#10-deployment-architecture)
11. [Future Considerations](#11-future-considerations)

---

## 1. System Overview

CodeMentor is a web application that accepts beginner code in Python or Java and returns structured, educational AI-generated feedback. The system is composed of three primary layers:

- A **React frontend** that handles user interaction and feedback display
- A **FastAPI backend** that validates input, enforces rate limits, and orchestrates calls to the Claude API
- The **Anthropic Claude API** as the AI reasoning engine

Optionally authenticated users can persist submission history via a **SQLite database** (PostgreSQL in production).

---

## 2. Architecture

### 2.1 High-Level Architecture

```
User (Browser)
     │
     │  HTTPS
     ▼
React Frontend (Vercel)
     │
     │  REST / JSON
     ▼
FastAPI Backend (Railway)
     ├──► Claude API (Anthropic)
     └──► SQLite / PostgreSQL
```

### 2.2 Architectural Pattern

The system follows a **client-server architecture** with a clear separation between:

- **Presentation layer** — React handles all UI rendering; no server-side HTML is generated
- **Application layer** — FastAPI handles business logic, validation, rate limiting, and API orchestration
- **Data layer** — SQLAlchemy ORM abstracts the database; only registered user data is persisted

This separation means the frontend and backend can be scaled, deployed, and tested independently.

### 2.3 Why Not a Monolith?

A Django monolith was considered and rejected for this project because:
- The frontend requires a reactive, component-driven UI that React handles better than Django templates
- The backend is purely an API — there is no server-rendered HTML, no admin panel, no complex ORM queries at this stage
- Separate deployment allows independent scaling (e.g. a traffic spike on the frontend doesn't affect backend resources)

---

## 3. Technology Decisions

### 3.1 Frontend: React + Tailwind CSS

**Decision:** React (JavaScript) with Tailwind CSS for styling, deployed on Vercel.

**Rationale:**
- React's component model maps well to the distinct UI sections (code input, feedback output, history panel)
- Tailwind enables rapid UI development without writing custom CSS files
- Vercel provides free, instant deployment from GitHub with zero configuration

**Alternatives considered:**
- Vue.js — similar capability but React has broader industry adoption in Australia
- Plain HTML/CSS/JS — insufficient for managing the multiple UI states this app requires

---

### 3.2 Backend: FastAPI

**Decision:** Python with FastAPI, deployed on Railway.

**Rationale:**
- FastAPI is purpose-built for API-only backends — exactly what this project requires
- Automatic OpenAPI (Swagger) documentation is generated without any additional work
- Pydantic models provide type-safe request and response validation out of the box
- FastAPI's async support means it handles concurrent Claude API calls efficiently
- Gaining traction in Australian industry, particularly for AI-adjacent services

**Alternatives considered:**
- Flask — simpler but no built-in type validation, no automatic docs, no async support
- Django — provides features (ORM, admin, templating) this project does not need; adds unnecessary complexity

---

### 3.3 AI Layer: Claude API

**Decision:** Anthropic Claude API using `claude-sonnet-4-20250514`.

**Rationale:**
- Claude is strong at following structured output instructions (returning JSON with named sections)
- The model handles code analysis and educational explanation well
- Sonnet 4 balances quality and cost appropriately for a low-budget personal project

**Key constraint:** The API key is stored as an environment variable server-side and is never exposed to the frontend.

---

### 3.4 Database: SQLite (dev) / PostgreSQL (prod)

**Decision:** SQLite for local development, PostgreSQL on Railway for production.

**Rationale:**
- SQLite requires zero infrastructure for development — no Docker, no setup
- SQLAlchemy ORM abstracts the database engine, so switching to PostgreSQL for production requires changing one connection string
- Submission history and user accounts have low write frequency — no need for a more complex database

---

## 4. Component Design

### 4.1 Frontend Components

```
src/
├── App.jsx                  # Root: routing, auth state
├── components/
│   ├── CodeInput.jsx        # Language selector + textarea + submit button
│   ├── ReviewOutput.jsx     # Three-section feedback display
│   ├── HistoryPanel.jsx     # Sidebar with past submissions (auth only)
│   └── Auth/
│       ├── LoginForm.jsx
│       └── RegisterForm.jsx
└── services/
    └── api.js               # All fetch() calls to the FastAPI backend
```

**State management:** React `useState` and `useContext` only — no Redux. The app state is simple enough that a global auth context plus local component state is sufficient.

---

### 4.2 Backend Modules

```
backend/
├── main.py                  # FastAPI app init, CORS config, router registration
├── routers/
│   └── review.py            # POST /review, GET /history endpoints
├── services/
│   ├── claude_service.py    # Claude API call + response parsing
│   └── prompt.py            # System prompt (version-controlled separately)
├── models/
│   ├── schemas.py           # Pydantic: ReviewRequest, ReviewResponse, UserCreate
│   └── db_models.py         # SQLAlchemy: User, Submission tables
├── db/
│   └── database.py          # SQLAlchemy engine + session factory
├── auth/
│   └── auth.py              # JWT token creation, password hashing (bcrypt)
└── middleware/
    └── rate_limit.py        # Sliding window rate limiter (IP + user-based)
```

---

## 5. Data Flow

### 5.1 Code Submission (Guest User)

```
1. User pastes code, selects language, clicks Submit
2. CodeInput.jsx → api.js → POST /review (JSON: {code, language, user_prompt})
3. FastAPI rate_limit middleware → check IP against Redis/in-memory store
4. FastAPI validates request via Pydantic schema (length, language enum)
5. claude_service.py constructs prompt (system prompt + user code)
6. Claude API returns structured JSON: {bugs, security, concepts}
7. FastAPI returns ReviewResponse to frontend
8. ReviewOutput.jsx renders three collapsible feedback cards
   (submission NOT saved to database for guest users)
```

### 5.2 Code Submission (Registered User)

Same as above, plus:
```
7a. SQLAlchemy saves Submission record linked to user_id
7b. HistoryPanel.jsx reflects new entry on next load
```

### 5.3 Authentication Flow

```
1. User submits email + password to POST /auth/register or POST /auth/login
2. FastAPI hashes password (bcrypt) on register, verifies hash on login
3. FastAPI returns JWT access token (expires 24h)
4. Frontend stores token in memory (not localStorage — avoids XSS risk)
5. Subsequent requests include token in Authorization: Bearer header
6. FastAPI validates token on protected routes (history, authenticated submissions)
```

---

## 6. Database Schema

### Users Table

| Column        | Type      | Constraints              |
|---------------|-----------|--------------------------|
| id            | UUID      | PRIMARY KEY              |
| email         | VARCHAR   | UNIQUE, NOT NULL         |
| password_hash | VARCHAR   | NOT NULL                 |
| created_at    | TIMESTAMP | DEFAULT now()            |

### Submissions Table

| Column           | Type      | Constraints              |
|------------------|-----------|--------------------------|
| id               | UUID      | PRIMARY KEY              |
| user_id          | UUID      | FK → users.id, NOT NULL  |
| language         | VARCHAR   | NOT NULL ('python'/'java')|
| code             | TEXT      | NOT NULL                 |
| user_prompt      | TEXT      | NULLABLE                 |
| feedback_bugs    | TEXT      | NOT NULL                 |
| feedback_security| TEXT      | NOT NULL                 |
| feedback_concepts| TEXT      | NOT NULL                 |
| created_at       | TIMESTAMP | DEFAULT now()            |

**Note:** Guest user submissions are not persisted. Code is only stored in the database for authenticated users who have explicitly opted into history by creating an account.

---

## 7. API Design

### Endpoints

| Method | Path              | Auth Required | Description                        |
|--------|-------------------|---------------|------------------------------------|
| POST   | /review           | No            | Submit code for review             |
| GET    | /history          | Yes           | Retrieve user's submission history |
| DELETE | /history/{id}     | Yes           | Delete a specific submission       |
| POST   | /auth/register    | No            | Create new account                 |
| POST   | /auth/login       | No            | Authenticate, receive JWT          |
| GET    | /docs             | No            | Auto-generated Swagger UI          |

### Request Schema: POST /review

```json
{
  "language": "python",
  "code": "def add(a, b):\n    return a + b",
  "user_prompt": "Can you check if this handles edge cases?"
}
```

### Response Schema: POST /review

```json
{
  "bugs": "Your function doesn't handle non-numeric inputs...",
  "security": "No security issues detected for this snippet.",
  "concepts": "This is a basic function definition. The 'def' keyword..."
}
```

### Error Responses

| Status | Scenario                        |
|--------|---------------------------------|
| 400    | Empty code, invalid language    |
| 413    | Code exceeds 5,000 characters   |
| 422    | Pydantic validation failure     |
| 429    | Rate limit exceeded             |
| 503    | Claude API unavailable          |

---

## 8. Prompt Engineering Strategy

The system prompt is the most critical component of this application. It lives in `backend/services/prompt.py` and is version-controlled independently of application logic so it can be iterated without touching routes or services.

### Design Principles

1. **Teach, don't fix.** The prompt instructs Claude to identify issues and explain the underlying concept, not to hand the user corrected code.
2. **Guide with questions.** For significant bugs, Claude is instructed to pose a guiding question that leads the user to the fix themselves.
3. **Beginner language.** Claude is instructed to avoid jargon without explanation and to assume the user is new to programming.
4. **Structured output.** Claude is instructed to return a JSON object with exactly three keys: `bugs`, `security`, `concepts`. This makes parsing deterministic.
5. **Prioritise.** Claude is instructed to surface the most important issue per section rather than overwhelming the user with every finding.

### Prompt Structure

```
SYSTEM:
You are CodeMentor, an educational code reviewer for beginner programmers.
Your role is to guide, not to fix.

When reviewing code, respond ONLY with valid JSON in exactly this format:
{
  "bugs": "...",
  "security": "...",
  "concepts": "..."
}

Rules:
- bugs: Identify correctness issues. Explain WHY it is a problem using beginner-friendly language.
  Ask a guiding question to help the user find the fix themselves. Do not provide the fixed code.
- security: Identify any security concerns relevant to a beginner (e.g. SQL injection, hardcoded credentials).
  If none, write: "No security issues detected in this snippet."
- concepts: Explain one core programming concept demonstrated or needed by this code.
  Define any technical terms you use.

Language: {language}

USER:
{code}

Additional context from user: {user_prompt}
```

---

## 9. Security Design

| Concern              | Mitigation                                                                 |
|----------------------|----------------------------------------------------------------------------|
| API key exposure     | Claude API key stored in `.env`, never sent to frontend                   |
| Password storage     | bcrypt hashing with cost factor 12                                         |
| JWT security         | Tokens stored in memory (not localStorage), 24h expiry                    |
| Input injection      | Pydantic validates all input; code is passed as a string value, not executed |
| CORS                 | Backend allows only the deployed Vercel frontend origin                    |
| Rate limiting        | 5/hour (guest by IP), 20/hour (registered by user ID)                     |
| Data minimisation    | Guest code is never stored; registered code stored only to support history |
| Prompt injection     | User code is placed inside a delimited string in the prompt, not inline   |

---

## 10. Deployment Architecture

```
GitHub (source of truth)
    │
    ├──► Vercel (auto-deploy on push to main)
    │         React build → CDN edge network
    │
    └──► Railway (auto-deploy on push to main)
              FastAPI server → persistent SQLite/PostgreSQL
              Environment variables: ANTHROPIC_API_KEY, DATABASE_URL, JWT_SECRET
```

**Environment variables required:**

| Variable           | Where        | Description                  |
|--------------------|--------------|------------------------------|
| ANTHROPIC_API_KEY  | Backend      | Anthropic Claude API key     |
| DATABASE_URL       | Backend      | SQLite (dev) or Postgres URL |
| JWT_SECRET         | Backend      | Secret key for signing JWTs  |
| VITE_API_URL       | Frontend     | Backend base URL             |

---

## 11. Future Considerations

These are explicitly out of scope for v1.0 but worth noting for future iterations:

- **Additional languages** — The language selector and prompt template are already parameterised; adding Java, C, or JavaScript is a minor change
- **Code execution sandbox** — Running user code in an isolated container (e.g. via Judge0 API) would allow feedback on runtime errors, not just static analysis
- **GitHub integration** — Allow users to submit a GitHub file URL rather than pasting code
- **Redis rate limiting** — Replace in-memory rate limiting with Redis for persistence across server restarts and horizontal scaling
- **PostgreSQL migration** — The SQLAlchemy ORM means this is a one-line connection string change