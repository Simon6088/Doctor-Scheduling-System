from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from .. import schemas, models
from .deps import get_db, get_current_admin_user

router = APIRouter()

@router.post("/departments/", response_model=schemas.Department)
def create_department(
    dept: schemas.DepartmentCreate, 
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_admin_user)
):
    db_dept = db.query(models.Department).filter(models.Department.name == dept.name).first()
    if db_dept:
        raise HTTPException(status_code=400, detail="Department already exists")
    
    new_dept = models.Department(
        name=dept.name,
        parent_id=dept.parent_id
    )
    db.add(new_dept)
    db.commit()
    db.refresh(new_dept)
    return new_dept

@router.get("/departments/", response_model=List[schemas.Department])
def read_departments(
    skip: int = 0, 
    limit: int = 100, 
    db: Session = Depends(get_db)
):
    depts = db.query(models.Department).offset(skip).limit(limit).all()
    return depts

@router.put("/departments/{dept_id}", response_model=schemas.Department)
def update_department(
    dept_id: int,
    dept_update: schemas.DepartmentCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_admin_user)
):
    db_dept = db.query(models.Department).filter(models.Department.id == dept_id).first()
    if not db_dept:
        raise HTTPException(status_code=404, detail="Department not found")
    
    db_dept.name = dept_update.name
    if dept_update.parent_id is not None:
        db_dept.parent_id = dept_update.parent_id
    
    db.commit()
    db.refresh(db_dept)
    return db_dept

@router.delete("/departments/{dept_id}")
def delete_department(
    dept_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_admin_user)
):
    db_dept = db.query(models.Department).filter(models.Department.id == dept_id).first()
    if not db_dept:
        raise HTTPException(status_code=404, detail="Department not found")
    
    db.delete(db_dept)
    db.commit()
    return {"message": "Department deleted successfully"}
