# Use Cases
## CodeMentor — AI-Powered Code Review for Beginner Programmers

**Version:** 1.0  
**Author:** Nour Zahrawi  
**Date:** May 2026  
**Status:** Approved

---

## Table of Contents

1. [Actors](#1-actors)
2. [Use Case Overview](#2-use-case-overview)
3. [Detailed Use Cases](#3-detailed-use-cases)
4. [Relationships Between Use Cases](#4-relationships-between-use-cases)

---

## 1. Actors

| Actor | Type | Description |
|-------|------|-------------|
| Guest User | Primary | A visitor who uses CodeMentor without an account. Can submit code and receive feedback. History is not saved. |
| Registered User | Primary | A user who has created an account and is logged in. Has full access to all features including submission history. Inherits all Guest User capabilities. |
| Claude API | Secondary | The Anthropic Claude API. Called by the system to analyse submitted code and return structured feedback. Does not initiate interactions. |

> Note: The System (FastAPI backend) is not listed as an actor. It is the subject of the use cases — the thing being described — not a participant initiating or receiving primary value.

---

## 2. Use Case Overview

| ID | Use Case | Guest User | Registered User | Claude API |
|----|----------|:----------:|:---------------:|:----------:|
| UC-01 | Submit code for review | ✓ | ✓ | |
| UC-02 | Receive structured feedback | ✓ | ✓ | |
| UC-03 | Register an account | ✓ | | |
| UC-04 | Log in | | ✓ | |
| UC-05 | View submission history | | ✓ | |
| UC-06 | Delete a history entry | | ✓ | |
| UC-07 | Analyse submitted code | | | ✓ |
| UC-08 | Return structured JSON response | | | ✓ |

---

## 3. Detailed Use Cases

---

### UC-01: Submit Code for Review

| Field | Detail |
|-------|--------|
| **ID** | UC-01 |
| **Name** | Submit code for review |
| **Actors** | Guest User, Registered User |
| **Preconditions** | User is on the main page. Rate limit has not been exceeded. |
| **Trigger** | User clicks the Submit button after entering code. |

**Main Success Flow:**
1. User selects a programming language (Python or Java) from the dropdown
2. User pastes or types code into the input area
3. User optionally enters a description of what they need help with
4. User clicks Submit
5. System validates the input — not empty, within 5,000 character limit, valid language
6. System checks the rate limit for the user's IP or account
7. System constructs the prompt and calls the Claude API (UC-07 included)
8. System receives structured JSON from Claude (UC-08 included)
9. System returns feedback to the frontend
10. User sees structured feedback rendered in three sections (UC-02)

**Alternative Flows:**

| Condition | System Response |
|-----------|-----------------|
| Code field is empty | Inline validation error shown; submission blocked |
| Code exceeds 5,000 characters | Character limit error shown with current count |
| Language not selected | Prompt to select a language before submitting |
| Rate limit exceeded | Message shown: "You've reached your limit. Try again in X minutes." |
| Claude API timeout or error | User-friendly error: "Something went wrong. Please try again." |

**Postconditions:**
- Feedback is displayed to the user
- If the user is a Registered User, the submission and feedback are saved to their history

---

### UC-02: Receive Structured Feedback

| Field | Detail |
|-------|--------|
| **ID** | UC-02 |
| **Name** | Receive structured feedback |
| **Actors** | Guest User, Registered User |
| **Preconditions** | UC-01 has completed successfully |
| **Trigger** | System receives valid JSON response from Claude API |

**Main Success Flow:**
1. System parses the JSON response into three sections: `bugs`, `security`, `concepts`
2. Frontend renders three collapsible cards, one per section
3. Each card displays the relevant feedback in readable prose
4. Code snippets within feedback are displayed in syntax-highlighted monospace blocks
5. A disclaimer is shown: "This feedback is AI-generated and may contain errors. Always verify with a trusted source."
6. If a section has no findings, the card shows: "Nothing to flag here."

**Alternative Flows:**

| Condition | System Response |
|-----------|-----------------|
| Claude returns malformed JSON | System attempts re-parse; on failure shows generic error |
| One section is missing from response | Missing section card shows a fallback message |

**Postconditions:**
- Feedback is visible and readable to the user
- Disclaimer is displayed on screen

---

### UC-03: Register an Account

| Field | Detail |
|-------|--------|
| **ID** | UC-03 |
| **Name** | Register an account |
| **Actors** | Guest User |
| **Preconditions** | User does not already have an account |
| **Trigger** | User clicks "Sign Up" and submits the registration form |

**Main Success Flow:**
1. User clicks "Sign Up" in the navigation
2. Registration form is displayed (email, password, confirm password)
3. User fills in fields and submits
4. System validates email format and checks it is not already registered
5. System validates password meets minimum strength requirements
6. System hashes the password with bcrypt and creates the user record
7. System returns a JWT access token
8. User is now logged in and redirected to the main page as a Registered User

**Alternative Flows:**

| Condition | System Response |
|-----------|-----------------|
| Email already registered | Error: "An account with this email already exists." |
| Password too weak | Inline error with strength requirements |
| Passwords do not match | Inline error on confirm password field |

**Postconditions:**
- User account exists in the database
- User is authenticated and session is active

---

### UC-04: Log In

| Field | Detail |
|-------|--------|
| **ID** | UC-04 |
| **Name** | Log in |
| **Actors** | Registered User |
| **Preconditions** | User has an existing account |
| **Trigger** | User clicks "Log In" and submits credentials |

**Main Success Flow:**
1. User clicks "Log In"
2. Login form is displayed (email, password)
3. User submits credentials
4. System looks up the email in the database
5. System verifies the submitted password against the stored bcrypt hash
6. System generates and returns a JWT access token (24-hour expiry)
7. Frontend stores the token in memory
8. User is now authenticated; history panel becomes visible

**Alternative Flows:**

| Condition | System Response |
|-----------|-----------------|
| Email not found | Generic error: "Invalid email or password." (avoids confirming which field is wrong) |
| Password incorrect | Generic error: "Invalid email or password." |
| Token expired on a later visit | User is silently logged out; prompted to log in again |

**Postconditions:**
- User is authenticated
- JWT token is held in memory for the session duration

---

### UC-05: View Submission History

| Field | Detail |
|-------|--------|
| **ID** | UC-05 |
| **Name** | View submission history |
| **Actors** | Registered User |
| **Preconditions** | User is logged in |
| **Trigger** | User navigates to the History panel or page |

**Main Success Flow:**
1. System queries the database for all submissions linked to the authenticated user's ID
2. Results are returned ordered by most recent first
3. History panel displays each submission as a row: language badge, timestamp, and code snippet preview
4. User clicks a row to expand and view the full feedback for that submission

**Alternative Flows:**

| Condition | System Response |
|-----------|-----------------|
| No submissions yet | Empty state: "You haven't submitted any code yet. Submit some to get started." |
| Database query fails | Error message with option to retry |

**Postconditions:**
- User can read past feedback without resubmitting

---

### UC-06: Delete a History Entry

| Field | Detail |
|-------|--------|
| **ID** | UC-06 |
| **Name** | Delete a history entry |
| **Actors** | Registered User |
| **Preconditions** | User is logged in and has at least one history entry |
| **Trigger** | User clicks the delete button on a history entry |

**Main Success Flow:**
1. User clicks the delete icon on a history entry
2. System shows a brief confirmation prompt: "Delete this submission? This cannot be undone."
3. User confirms
4. System sends DELETE /history/{id} to the backend
5. Backend verifies the submission belongs to the authenticated user before deleting
6. Record is removed from the database
7. History panel updates to remove the deleted entry

**Alternative Flows:**

| Condition | System Response |
|-----------|-----------------|
| User cancels confirmation | No action taken |
| Submission ID does not belong to authenticated user | 403 Forbidden returned; no deletion occurs |

**Postconditions:**
- Submission record no longer exists in the database

---

### UC-07: Analyse Submitted Code (Claude API)

| Field | Detail |
|-------|--------|
| **ID** | UC-07 |
| **Name** | Analyse submitted code |
| **Actors** | Claude API |
| **Preconditions** | UC-01 validation has passed; prompt has been constructed |
| **Trigger** | System calls the Claude API with the constructed prompt |
| **Relationship** | Included by UC-01 |

**Main Success Flow:**
1. System sends POST request to Claude API with system prompt and user code
2. Claude analyses the code for bugs, security issues, and teachable concepts
3. Claude applies the educational guidelines from the system prompt (guide, don't fix)
4. Claude generates a response in the required JSON structure

**Postconditions:**
- A structured JSON object is ready to be returned (UC-08)

---

### UC-08: Return Structured JSON Response (Claude API)

| Field | Detail |
|-------|--------|
| **ID** | UC-08 |
| **Name** | Return structured JSON response |
| **Actors** | Claude API |
| **Preconditions** | UC-07 has completed |
| **Trigger** | Claude API sends response back to FastAPI backend |
| **Relationship** | Included by UC-02 |

**Main Success Flow:**
1. Claude API returns HTTP 200 with a JSON body
2. Body contains exactly three keys: `bugs`, `security`, `concepts`
3. FastAPI backend receives and validates the response structure
4. Validated response is forwarded to the frontend

**Alternative Flows:**

| Condition | System Response |
|-----------|-----------------|
| API returns non-200 status | Backend catches error, returns 503 to frontend |
| Response missing a required key | Backend returns fallback text for the missing section |

**Postconditions:**
- Frontend has the data needed to render UC-02

---

## 4. Relationships Between Use Cases

| Relationship | Type | Description |
|--------------|------|-------------|
| UC-01 → UC-07 | «include» | Submitting code always triggers a Claude API call |
| UC-02 → UC-08 | «include» | Displaying feedback always requires the structured JSON response |
| UC-05 → UC-01 | «extend» | Viewing history is only meaningful if the user has submitted code before |
| Registered User → Guest User | Generalisation | Registered users inherit all Guest User capabilities and gain additional ones |