from typing import List, Optional
from datetime import date, timedelta
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from .. import schemas, models
from ..core.scheduler import SchedulingEngine
from .deps import get_db, get_current_user, get_current_admin_user
from .audit import log_action

router = APIRouter()

@router.post("/schedules/generate", response_model=List[schemas.ScheduleSchema])
def generate_schedule(
    start_date: date,
    days: int = 30,
    department_id: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_admin_user)
):
    # 1. Fetch Resources
    query = db.query(models.User).filter(models.User.role == models.RoleEnum.DOCTOR)
    if department_id:
        query = query.filter(models.User.department_id == department_id)
    doctors = query.all()
    
    if not doctors:
        raise HTTPException(status_code=400, detail="No doctors found for scheduling")

    shift_types = db.query(models.ShiftType).all()
    if not shift_types:
        day_shift = models.ShiftType(name="Day Shift", start_time="08:00", end_time="17:00")
        night_shift = models.ShiftType(name="Night Shift", start_time="17:00", end_time="08:00")
        db.add(day_shift)
        db.add(night_shift)
        db.commit()
        shift_types = [day_shift, night_shift]
    
    # 2. Run Engine
    engine = SchedulingEngine(doctors, shift_types, start_date, days)
    engine.build_model()
    results = engine.solve()
    
    if not results:
        raise HTTPException(status_code=400, detail="Infeasible schedule. Too many constraints?")
    
    # 3. Save to DB (Draft status)
    saved_schedules = []
    for item in results:
        existing = db.query(models.Schedule).filter(
            models.Schedule.date == item['date'],
            models.Schedule.shift_type_id == item['shift_type_id'],
            models.Schedule.doctor_id == item['doctor_id']
        ).first()
        
        if existing:
            continue
            
        new_sched = models.Schedule(
            date=item['date'],
            doctor_id=item['doctor_id'],
            shift_type_id=item['shift_type_id'],
            status="draft"
        )
        db.add(new_sched)
        saved_schedules.append(new_sched)
    
    db.commit()
    
    log_action(db, current_user.id, "GENERATE", "schedule", details=f"Generated {len(saved_schedules)} shifts from {start_date}")
    
    return saved_schedules

@router.post("/schedules/publish")
def publish_schedules(
    start_date: date,
    end_date: date,
    department_id: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_admin_user)
):
    query = db.query(models.Schedule).filter(
        models.Schedule.date >= start_date,
        models.Schedule.date <= end_date,
        models.Schedule.status == 'draft'
    )
    
    if department_id:
        query = query.join(models.User).filter(models.User.department_id == department_id)
        
    count = query.update({models.Schedule.status: 'published'}, synchronize_session=False)
    db.commit()
    
    log_action(db, current_user.id, "PUBLISH", "schedule", details=f"Published {count} schedules from {start_date} to {end_date}")
    return {"message": f"Successfully published {count} schedules"}

@router.get("/schedules/", response_model=List[schemas.ScheduleSchema])
def read_schedules(
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    doctor_id: Optional[int] = None,
    department_id: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    query = db.query(models.Schedule)
    
    # Non-admins can only see published schedules
    if current_user.role != models.RoleEnum.ADMIN:
        query = query.filter(models.Schedule.status == "published")
        
    if start_date:
        query = query.filter(models.Schedule.date >= start_date)
    if end_date:
        query = query.filter(models.Schedule.date <= end_date)
    if doctor_id:
        query = query.filter(models.Schedule.doctor_id == doctor_id)
        
    if department_id:
        query = query.join(models.User).filter(models.User.department_id == department_id)
        
    schedules = query.all()
    return schedules

@router.delete("/schedules/{schedule_id}")
def delete_schedule(
    schedule_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_admin_user)
):
    schedule = db.query(models.Schedule).filter(models.Schedule.id == schedule_id).first()
    if not schedule:
        raise HTTPException(status_code=404, detail="Schedule not found")
    
    db.delete(schedule)
    db.commit()
    
    log_action(db, current_user.id, "DELETE", "schedule", str(schedule_id), f"Deleted schedule {schedule_id}")
    return {"message": "Schedule deleted successfully"}
