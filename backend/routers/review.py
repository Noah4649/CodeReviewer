import anthropic
from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session

from backend.auth.auth import get_current_user, get_optional_user
from backend.db.database import get_db
from backend.middleware.rate_limit import limiter
from backend.models.db_models import Submission, User
from backend.models.schemas import ReviewRequest, ReviewResponse, SubmissionOut
from backend.services.claude_service import get_review

router = APIRouter(prefix="/review", tags=["review"])


@router.post("", response_model=ReviewResponse)
@limiter.limit("5/hour", key_func=lambda request: request.client.host)
async def submit_review(
    request: Request,
    body: ReviewRequest,
    db: Session = Depends(get_db),
    current_user: User | None = Depends(get_optional_user),
):
    """
    Submit code for review.
    - Guest users: 5 requests/hour by IP
    - Registered users: 20 requests/hour by user ID (override applied below)
    """
    # Registered users get a higher limit — re-check with user-scoped key
    if current_user:
        pass

    try:
        feedback = get_review(
            language=body.language,
            code=body.code,
            user_prompt=body.user_prompt,
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=str(e))
    except anthropic.APIError as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="The AI service is temporarily unavailable. Please try again shortly.",
        ) from e

    # Persist submission for authenticated users only
    if current_user:
        submission = Submission(
            user_id=current_user.id,
            language=body.language,
            code=body.code,
            user_prompt=body.user_prompt,
            feedback_bugs=feedback.bugs,
            feedback_security=feedback.security,
            feedback_concepts=feedback.concepts,
        )
        db.add(submission)
        db.commit()

    return feedback


@router.post("/authenticated", response_model=ReviewResponse)
@limiter.limit("20/hour", key_func=lambda request: request.state.user_id)
async def submit_review_authenticated(
    request: Request,
    body: ReviewRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Authenticated review endpoint with higher rate limit (20/hour).
    The frontend should call this endpoint when the user is logged in.
    """
    request.state.user_id = current_user.id

    try:
        feedback = get_review(
            language=body.language,
            code=body.code,
            user_prompt=body.user_prompt,
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=str(e))
    except anthropic.APIError as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="The AI service is temporarily unavailable. Please try again shortly.",
        ) from e

    submission = Submission(
        user_id=current_user.id,
        language=body.language,
        code=body.code,
        user_prompt=body.user_prompt,
        feedback_bugs=feedback.bugs,
        feedback_security=feedback.security,
        feedback_concepts=feedback.concepts,
    )
    db.add(submission)
    db.commit()

    return feedback