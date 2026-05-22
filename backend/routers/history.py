from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from backend.auth.auth import get_current_user
from backend.db.database import get_db
from backend.models.db_models import Submission, User
from backend.models.schemas import SubmissionOut

router = APIRouter(prefix="/history", tags=["history"])


@router.get("", response_model=list[SubmissionOut])
def get_history(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Return all submissions for the authenticated user, most recent first."""
    submissions = (
        db.query(Submission)
        .filter(Submission.user_id == current_user.id)
        .order_by(Submission.created_at.desc())
        .all()
    )
    return submissions


@router.delete("/{submission_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_submission(
    submission_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Delete a specific submission. Only the owner can delete their own entries."""
    submission = db.query(Submission).filter(Submission.id == submission_id).first()

    if submission is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Submission not found.")

    # Ownership check — critical security gate
    if submission.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to delete this submission.",
        )

    db.delete(submission)
    db.commit()