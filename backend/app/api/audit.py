from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List, Optional
from .. import models, schemas
from .deps import get_db, get_current_admin_user

router = APIRouter(prefix="/audit-logs", tags=["audit"])

def log_action(db: Session, user_id: int, action: str, resource: str, resource_id: str = None, details: str = None):
    try:
        log = models.AuditLog(
            user_id=user_id,
            action=action,
            resource=resource,
            resource_id=str(resource_id) if resource_id else None,
            details=details
        )
        db.add(log)
        db.commit()
    except Exception as e:
        print(f"Audit log failed: {e}")

@router.get("/", response_model=List[schemas.AuditLog])
def list_audit_logs(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_admin_user),
    limit: int = 100
):
    return db.query(models.AuditLog).order_by(models.AuditLog.created_at.desc()).limit(limit).all()
