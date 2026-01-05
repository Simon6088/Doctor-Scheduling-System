from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from .. import models, schemas
from .deps import get_db, get_current_admin_user

router = APIRouter(prefix="/tags", tags=["tags"])

@router.get("/", response_model=List[schemas.Tag])
def list_tags(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_admin_user)
):
    return db.query(models.Tag).all()

@router.post("/", response_model=schemas.Tag)
def create_tag(
    tag: schemas.TagCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_admin_user)
):
    db_tag = models.Tag(**tag.dict())
    db.add(db_tag)
    db.commit()
    db.refresh(db_tag)
    return db_tag

@router.delete("/{tag_id}")
def delete_tag(
    tag_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_admin_user)
):
    tag = db.query(models.Tag).filter(models.Tag.id == tag_id).first()
    if not tag:
        raise HTTPException(status_code=404, detail="Tag not found")
    db.delete(tag)
    db.commit()
    return {"status": "success"}

@router.post("/{tag_id}/users/{user_id}")
def assign_tag_to_user(
    tag_id: int,
    user_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_admin_user)
):
    tag = db.query(models.Tag).filter(models.Tag.id == tag_id).first()
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not tag or not user:
        raise HTTPException(status_code=404, detail="Tag or User not found")
    
    if tag not in user.tags:
        user.tags.append(tag)
        db.commit()
        
    return {"status": "assigned"}

@router.delete("/{tag_id}/users/{user_id}")
def remove_tag_from_user(
    tag_id: int,
    user_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_admin_user)
):
    tag = db.query(models.Tag).filter(models.Tag.id == tag_id).first()
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not tag or not user:
        raise HTTPException(status_code=404, detail="Tag or User not found")
        
    if tag in user.tags:
        user.tags.remove(tag)
        db.commit()
        
    return {"status": "removed"}
