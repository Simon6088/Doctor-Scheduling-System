from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from .. import models, schemas
from .deps import get_db, get_current_user, get_current_admin_user

router = APIRouter(prefix="/feedback", tags=["feedback"])

@router.post("/", response_model=schemas.FeedbackResponse)
def create_feedback(
    feedback: schemas.FeedbackCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    db_feedback = models.Feedback(
        **feedback.dict(),
        user_id=current_user.id
    )
    db.add(db_feedback)
    db.commit()
    db.refresh(db_feedback)
    return db_feedback

@router.get("/", response_model=List[schemas.FeedbackResponse])
def list_feedbacks(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_admin_user)
):
    return db.query(models.Feedback).order_by(models.Feedback.created_at.desc()).all()

@router.put("/{feedback_id}/close", response_model=schemas.FeedbackResponse)
def close_feedback(
    feedback_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_admin_user)
):
    feedback = db.query(models.Feedback).filter(models.Feedback.id == feedback_id).first()
    if not feedback:
        raise HTTPException(status_code=404, detail="Feedback not found")
    feedback.status = "closed"
    db.commit()
    db.refresh(feedback)
    return feedback
