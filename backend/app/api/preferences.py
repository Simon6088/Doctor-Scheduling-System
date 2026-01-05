from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from .. import schemas, models
from .deps import get_db, get_current_user, get_current_admin_user

router = APIRouter()

@router.post("/preferences/", response_model=schemas.PreferenceResponse)
def create_preference(
    pref: schemas.PreferenceCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    new_pref = models.Preference(
        user_id=current_user.id,
        date=pref.date,
        type=pref.type,
        shift_type_id=pref.shift_type_id,
        reason=pref.reason
    )
    db.add(new_pref)
    db.commit()
    db.refresh(new_pref)
    return new_pref

@router.get("/preferences/me", response_model=List[schemas.PreferenceResponse])
def get_my_preferences(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    return db.query(models.Preference).filter(models.Preference.user_id == current_user.id).order_by(models.Preference.date).all()

@router.get("/preferences/", response_model=List[schemas.PreferenceResponse])
def get_all_preferences(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_admin_user)
):
    return db.query(models.Preference).all()

@router.delete("/preferences/{pref_id}")
def delete_preference(
    pref_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    pref = db.query(models.Preference).filter(models.Preference.id == pref_id).first()
    if not pref:
        raise HTTPException(status_code=404, detail="Preference not found")
    
    # Only owner or admin can delete
    if pref.user_id != current_user.id and current_user.role != models.RoleEnum.ADMIN:
        raise HTTPException(status_code=403, detail="Not authorized")
        
    db.delete(pref)
    db.commit()
    return {"message": "Preference deleted"}
