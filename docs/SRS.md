# Software Requirements Specification
## CodeMentor — AI-Powered Code Review for Beginner Programmers

**Version:** 1.0  
**Author:** Nour Zahrawi  
**Date:** May 2026  
**Status:** Approved

---

## Table of Contents

1. [Introduction](#1-introduction)
2. [Overall Description](#2-overall-description)
3. [Actors](#3-actors)
4. [Functional Requirements](#4-functional-requirements)
5. [Non-Functional Requirements](#5-non-functional-requirements)
6. [Use Cases](#6-use-cases)
7. [Data Requirements](#7-data-requirements)
8. [Constraints and Assumptions](#8-constraints-and-assumptions)
9. [Out of Scope](#9-out-of-scope)

---

## 1. Introduction

### 1.1 Purpose

This document specifies the software requirements for **CodeMentor**, a web-based application that provides AI-powered code review guidance for beginner programmers. It is intended to serve as the authoritative reference for design, development, and testing decisions throughout the project lifecycle.

### 1.2 Scope

CodeMentor allows users to submit code written in Python or Java and receive structured, educational feedback broken into three categories: correctness and bugs, security issues, and concept explanations. The system is designed to teach — not to hand users a fixed solution — by guiding them toward understanding the problem themselves.

The application exposes a React-based frontend, a FastAPI backend, and integrates with the Anthropic Claude API for AI-generated feedback. Authenticated users may optionally save and revisit their submission history.

### 1.3 Definitions

| Term | Definition |
|------|------------|
| Submission | A single instance of a user submitting code for review |
| Feedback | The structured AI-generated response returned for a submission |
| Guest user | A user who has not logged in |
| Registered user | A user who has created an account and is logged in |
| Rate limit | A cap on the number of submissions allowed per user/IP within a time window |

### 1.4 References

- Anthropic Claude API Documentation — https://docs.anthropic.com
- FastAPI Documentation — https://fastapi.tiangolo.com
- React Documentation — https://react.dev
- OWASP Top 10 — https://owasp.org/www-project-top-ten

---

## 2. Overall Description

### 2.1 Product Perspective

CodeMentor is a standalone web application. It does not integrate with any learning management system, IDE, or version control platform at this stage. The Claude API is the sole external AI dependency.

### 2.2 Product Functions (Summary)

- Accept code submissions in Python or Java
- Return structured feedback across three categories: bugs, security, and concepts
- Rate-limit submissions to prevent abuse
- Display a disclaimer that feedback is AI-generated
- Allow optional account creation to persist submission history

### 2.3 User Characteristics

The primary user is a beginner programmer — likely a first or second year university student or a self-taught learner — who is uncomfortable reading raw compiler errors or understanding why their code is wrong. They are not expected to have prior experience with code review tools.

### 2.4 Operating Environment

- **Frontend:** Any modern browser (Chrome, Firefox, Safari, Edge)
- **Backend:** Python 3.11+, FastAPI, deployed on Railway or equivalent
- **Frontend hosting:** Vercel
- **Database:** SQLite (development), PostgreSQL (production)
- **External API:** Anthropic Claude API (claude-sonnet-4-20250514)

---

## 3. Actors

| Actor | Description |
|-------|-------------|
| **Guest User** | Visits the site without logging in. Can submit code and receive feedback but history is not saved. |
| **Registered User** | Has created an account. Can submit code, receive feedback, and view past submissions. |
| **System** | The FastAPI backend. Validates input, enforces rate limits, communicates with Claude API, and returns structured feedback. |
| **Claude API** | External AI service. Receives the prompt constructed by the system and returns educational feedback. |

---

## 4. Functional Requirements

Requirements are labelled FR-XX. Priority: **H** = High (must have), **M** = Medium (should have), **L** = Low (nice to have).

### 4.1 Code Submission

| ID | Requirement | Priority |
|----|-------------|----------|
| FR-01 | The system shall provide a text input area where users can paste or type code | H |
| FR-02 | The system shall provide a language selector limited to Python and Java at launch | H |
| FR-03 | The system shall provide an optional free-text field for the user to describe what they need help with | M |
| FR-04 | The system shall reject submissions where the code input is empty | H |
| FR-05 | The system shall reject submissions exceeding 5,000 characters and display an informative error message | H |
| FR-06 | The system shall display a loading state while awaiting a response from the Claude API | H |

### 4.2 Feedback Display

| ID | Requirement | Priority |
|----|-------------|----------|
| FR-07 | The system shall return feedback structured into three labelled sections: **Bugs & Correctness**, **Security Issues**, and **Concept Explanation** | H |
| FR-08 | Each feedback section shall be displayed in a visually distinct, collapsible card | M |
| FR-09 | The system shall render code snippets within feedback in a monospaced, syntax-highlighted block | M |
| FR-10 | The system shall display a disclaimer on every feedback response stating that the output is AI-generated and may contain errors | H |
| FR-11 | If a section has no findings (e.g. no security issues detected), the system shall display a clear "nothing to flag here" message rather than leaving the section empty | M |

### 4.3 Authentication & Accounts

| ID | Requirement | Priority |
|----|-------------|----------|
| FR-12 | The system shall allow users to register with an email address and password | M |
| FR-13 | The system shall allow registered users to log in and log out | M |
| FR-14 | The system shall allow guest users to use the tool fully without creating an account | H |
| FR-15 | Registered users shall be able to view a history of their past submissions and the corresponding feedback | M |
| FR-16 | Registered users shall be able to delete individual entries from their history | L |

### 4.4 Rate Limiting

| ID | Requirement | Priority |
|----|-------------|----------|
| FR-17 | Guest users shall be limited to **5 submissions per hour** per IP address | H |
| FR-18 | Registered users shall be limited to **20 submissions per hour** per account | H |
| FR-19 | When a rate limit is reached, the system shall display a clear message indicating when the user may submit again | H |

---

## 5. Non-Functional Requirements

### 5.1 Performance

| ID | Requirement |
|----|-------------|
| NFR-01 | The system shall return feedback within 15 seconds for 95% of submissions under normal load |
| NFR-02 | The frontend shall display a loading indicator within 300ms of submission |

### 5.2 Usability

| ID | Requirement |
|----|-------------|
| NFR-03 | A first-time user shall be able to submit code and receive feedback without any instructions |
| NFR-04 | The interface shall be fully usable on both desktop and mobile screen sizes |
| NFR-05 | Feedback language shall avoid unnecessary jargon; technical terms shall be explained inline |

### 5.3 Security

| ID | Requirement |
|----|-------------|
| NFR-06 | The Claude API key shall never be exposed to the frontend; all API calls are made server-side |
| NFR-07 | User passwords shall be hashed using bcrypt before storage |
| NFR-08 | The system shall sanitise all user input before constructing the Claude API prompt |
| NFR-09 | Submitted code shall not be stored for guest users beyond the duration of the session |
| NFR-10 | The backend shall implement CORS restrictions, allowing only the deployed frontend origin |

### 5.4 Maintainability

| ID | Requirement |
|----|-------------|
| NFR-11 | The system prompt used to instruct Claude shall be maintained in a dedicated, version-controlled file separate from application logic |
| NFR-12 | All API routes shall be documented via FastAPI's automatic OpenAPI (Swagger) interface |

### 5.5 Reliability

| ID | Requirement |
|----|-------------|
| NFR-13 | If the Claude API returns an error or times out, the system shall display a user-friendly error message and not crash |
| NFR-14 | The application shall target 99% uptime during normal operating conditions |

---

## 6. Use Cases

### UC-01: Submit Code for Review

| Field | Detail |
|-------|--------|
| **Actor** | Guest User or Registered User |
| **Precondition** | User is on the main page |
| **Trigger** | User pastes code, selects a language, and clicks Submit |
| **Main Flow** | 1. User selects Python or Java from the language dropdown 2. User pastes code into the input area 3. User optionally describes what they need help with 4. User clicks Submit 5. System validates input (not empty, under 5,000 chars, within rate limit) 6. System constructs prompt and sends to Claude API 7. System parses response into three sections 8. System displays structured feedback with disclaimer |
| **Alternative Flow A** | Input is empty → system shows inline validation error, does not submit |
| **Alternative Flow B** | Code exceeds 5,000 characters → system shows character limit error |
| **Alternative Flow C** | Rate limit reached → system shows cooldown message with time remaining |
| **Alternative Flow D** | Claude API times out → system shows error message, invites retry |
| **Postcondition** | Feedback is displayed. If user is registered, submission is saved to history. |

---

### UC-02: Register an Account

| Field | Detail |
|-------|--------|
| **Actor** | Guest User |
| **Precondition** | User does not have an account |
| **Trigger** | User clicks "Sign Up" |
| **Main Flow** | 1. User enters email and password 2. System validates email format and password strength 3. System hashes password and creates account 4. User is logged in and redirected to main page |
| **Alternative Flow** | Email already registered → system shows error message |
| **Postcondition** | User is authenticated and future submissions are saved |

---

### UC-03: View Submission History

| Field | Detail |
|-------|--------|
| **Actor** | Registered User |
| **Precondition** | User is logged in and has at least one past submission |
| **Trigger** | User navigates to History page |
| **Main Flow** | 1. System retrieves submissions from database for the logged-in user 2. System displays list ordered by most recent first 3. User clicks a submission to expand and view the full feedback |
| **Alternative Flow** | No submissions yet → system displays an empty state message encouraging first submission |
| **Postcondition** | User can review past feedback |

---

## 7. Data Requirements

### 7.1 Submission Record (Registered Users Only)

| Field | Type | Description |
|-------|------|-------------|
| id | UUID | Unique submission identifier |
| user_id | FK | Reference to the user who submitted |
| language | String | "python" or "java" |
| code | Text | The submitted code |
| user_prompt | String (nullable) | Optional context provided by user |
| feedback_bugs | Text | Bugs & Correctness section of feedback |
| feedback_security | Text | Security Issues section of feedback |
| feedback_concepts | Text | Concept Explanation section of feedback |
| created_at | DateTime | Timestamp of submission |

### 7.2 User Record

| Field | Type | Description |
|-------|------|-------------|
| id | UUID | Unique user identifier |
| email | String | Unique, used for login |
| password_hash | String | bcrypt hash |
| created_at | DateTime | Account creation timestamp |

---

## 8. Constraints and Assumptions

- The application is dependent on the Anthropic Claude API being available; no offline mode is planned
- Claude API costs are borne by the developer; rate limiting exists partly to control spend
- At launch, only Python and Java are supported; additional languages may be added in a future version
- The application is not intended to replace formal code review or professional security auditing
- Users are assumed to have a basic understanding of how to copy and paste code

---

## 9. Out of Scope

The following are explicitly excluded from version 1.0:

- Code execution or running code in a sandbox
- Support for languages other than Python and Java
- IDE plugins or browser extensions
- Integration with GitHub, GitLab, or any version control platform
- Real-time collaborative review
- Automated testing of submitted code against test cases
- Paid tiers or subscription management