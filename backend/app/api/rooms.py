from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from .. import schemas, models
from .deps import get_db, get_current_user, get_current_admin_user

router = APIRouter()

@router.get("/rooms/", response_model=List[schemas.RoomResponse])
def get_rooms(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """获取所有诊室"""
    return db.query(models.Room).all()

@router.post("/rooms/", response_model=schemas.RoomResponse)
def create_room(
    room: schemas.RoomCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_admin_user)
):
    """创建诊室 - 仅管理员"""
    # 检查房间号是否已存在
    existing = db.query(models.Room).filter(models.Room.room_number == room.room_number).first()
    if existing:
        raise HTTPException(status_code=400, detail="Room number already exists")
    
    db_room = models.Room(**room.model_dump())
    db.add(db_room)
    db.commit()
    db.refresh(db_room)
    return db_room

@router.put("/rooms/{room_id}", response_model=schemas.RoomResponse)
def update_room(
    room_id: int,
    room: schemas.RoomUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_admin_user)
):
    """更新诊室 - 仅管理员"""
    db_room = db.query(models.Room).filter(models.Room.id == room_id).first()
    if not db_room:
        raise HTTPException(status_code=404, detail="Room not found")
    
    update_data = room.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_room, key, value)
    
    db.commit()
    db.refresh(db_room)
    return db_room

@router.delete("/rooms/{room_id}")
def delete_room(
    room_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_admin_user)
):
    """删除诊室 - 仅管理员"""
    db_room = db.query(models.Room).filter(models.Room.id == room_id).first()
    if not db_room:
        raise HTTPException(status_code=404, detail="Room not found")
    
    # 检查是否有排班使用此诊室
    schedules_count = db.query(models.Schedule).filter(models.Schedule.room_id == room_id).count()
    if schedules_count > 0:
        raise HTTPException(status_code=400, detail=f"Cannot delete room with {schedules_count} schedules")
    
    db.delete(db_room)
    db.commit()
    return {"message": "Room deleted successfully"}
