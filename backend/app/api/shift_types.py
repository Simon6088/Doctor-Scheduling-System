from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from .. import schemas, models
from .deps import get_db, get_current_admin_user, get_current_user

router = APIRouter()

@router.get("/shift-types/", response_model=List[schemas.ShiftTypeSchema])
def read_shift_types(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """获取所有班次类型"""
    return db.query(models.ShiftType).all()

@router.post("/shift-types/", response_model=schemas.ShiftTypeSchema)
def create_shift_type(
    shift_type: schemas.ShiftTypeCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_admin_user)
):
    """创建班次类型"""
    db_shift_type = models.ShiftType(**shift_type.model_dump())
    db.add(db_shift_type)
    db.commit()
    db.refresh(db_shift_type)
    return db_shift_type

@router.put("/shift-types/{shift_type_id}", response_model=schemas.ShiftTypeSchema)
def update_shift_type(
    shift_type_id: int,
    shift_type: schemas.ShiftTypeUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_admin_user)
):
    """更新班次类型"""
    db_shift_type = db.query(models.ShiftType).filter(models.ShiftType.id == shift_type_id).first()
    if not db_shift_type:
        raise HTTPException(status_code=404, detail="Shift type not found")
    
    update_data = shift_type.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_shift_type, key, value)
    
    db.commit()
    db.refresh(db_shift_type)
    return db_shift_type

@router.delete("/shift-types/{shift_type_id}")
def delete_shift_type(
    shift_type_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_admin_user)
):
    """删除班次类型"""
    db_shift_type = db.query(models.ShiftType).filter(models.ShiftType.id == shift_type_id).first()
    if not db_shift_type:
        raise HTTPException(status_code=404, detail="Shift type not found")
    
    # 检查是否有排班使用此班次
    schedules_count = db.query(models.Schedule).filter(models.Schedule.shift_type_id == shift_type_id).count()
    if schedules_count > 0:
        raise HTTPException(status_code=400, detail=f"Cannot delete shift type: {schedules_count} schedules are using it")
    
    db.delete(db_shift_type)
    db.commit()
    return {"message": "Shift type deleted successfully"}
