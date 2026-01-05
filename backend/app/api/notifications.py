from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from .. import models, schemas
from .deps import get_db, get_current_user

router = APIRouter(prefix="/notifications", tags=["notifications"])

@router.get("/", response_model=List[schemas.NotificationResponse])
def read_notifications(
    skip: int = 0, 
    limit: int = 50, 
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """Get my notifications"""
    return db.query(models.Notification)\
             .filter(models.Notification.user_id == current_user.id)\
             .order_by(models.Notification.created_at.desc())\
             .offset(skip).limit(limit).all()

@router.put("/{notification_id}/read")
def mark_read(
    notification_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    notif = db.query(models.Notification).filter(models.Notification.id == notification_id).first()
    if not notif:
        raise HTTPException(status_code=404, detail="Notification not found")
    if notif.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not permitted")
        
    notif.is_read = True
    db.commit()
    return {"status": "success"}

@router.get("/unread-count")
def get_unread_count(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    count = db.query(models.Notification)\
              .filter(models.Notification.user_id == current_user.id, models.Notification.is_read == False)\
              .count()
    return {"count": count}
