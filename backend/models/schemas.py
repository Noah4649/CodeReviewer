from datetime import datetime
from pydantic import BaseModel, EmailStr, field_validator
from typing import Literal

SUPPORTED_LANGUAGES = Literal["python", "java"]
MAX_CODE_LENGTH = 5000


# ── Review ────────────────────────────────────────────────────────────────────

class ReviewRequest(BaseModel):
    language: SUPPORTED_LANGUAGES
    code: str
    user_prompt: str | None = None

    @field_validator("code")
    @classmethod
    def code_must_not_be_empty(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("Code cannot be empty.")
        if len(v) > MAX_CODE_LENGTH:
            raise ValueError(
                f"Code exceeds the {MAX_CODE_LENGTH:,} character limit "
                f"({len(v):,} characters submitted)."
            )
        return v


class ReviewResponse(BaseModel):
    bugs: str
    security: str
    concepts: str


# ── Auth ──────────────────────────────────────────────────────────────────────

class UserCreate(BaseModel):
    email: EmailStr
    password: str

    @field_validator("password")
    @classmethod
    def password_strength(cls, v: str) -> str:
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters.")
        return v


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


# ── History ───────────────────────────────────────────────────────────────────

class SubmissionOut(BaseModel):
    id: str
    language: str
    code: str
    user_prompt: str | None
    feedback_bugs: str
    feedback_security: str
    feedback_concepts: str
    created_at: datetime

    model_config = {"from_attributes": True}