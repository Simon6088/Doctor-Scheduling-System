from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Optional, Dict, Any
from datetime import date
from .. import models
from .deps import get_db, get_current_user, get_current_admin_user, get_current_manager_user

router = APIRouter()

@router.get("/stats/workload")
def get_workload_stats(
    start_date: date,
    end_date: date,
    department_id: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_manager_user)
):
    """
    Get workload statistics for doctors within a date range.
    Returns: List of objects with doctor details and shift counts.
    """
    # Enforce permission for Managers
    if current_user.role == models.RoleEnum.DEPARTMENT_MANAGER:
         if department_id and department_id != current_user.department_id:
             raise HTTPException(status_code=403, detail="Managers can only view their own department stats")
         department_id = current_user.department_id
    
    # 1. Fetch data
    query = db.query(
        models.Schedule,
        models.User,
        models.ShiftType
    ).join(models.User, models.Schedule.doctor_id == models.User.id)\
     .join(models.ShiftType, models.Schedule.shift_type_id == models.ShiftType.id)\
     .filter(
        models.Schedule.date >= start_date,
        models.Schedule.date <= end_date
    )
    
    if department_id:
        query = query.filter(models.User.department_id == department_id)
        
    results = query.all()
    
    # 2. Process Statistics
    stats_map = {} # doctor_id -> { stats }
    
    user_query = db.query(models.User)
    if department_id:
        user_query = user_query.filter(models.User.department_id == department_id)
    all_users = user_query.all()
    
    for user in all_users:
        stats_map[user.id] = {
            "doctor_id": user.id,
            "doctor_name": user.full_name,
            "department_id": user.department_id,
            "total_shifts": 0,
            "night_shifts": 0,
            "weekend_shifts": 0,
            "holiday_shifts": 0
        }
        
    # Helper for holidays (MVP: Hardcoded for demo)
    def is_holiday(d: date) -> bool:
        # Month, Day tuples
        holidays = [
            (1, 1), # New Year
            (5, 1), (5, 2), (5, 3), # Labor Day
            (10, 1), (10, 2), (10, 3) # National Day
        ]
        # In real app, this should query a Calendar/Holiday table
        return (d.month, d.day) in holidays

    for schedule, user, shift_type in results:
        if user.id not in stats_map:
            continue 
            
        entry = stats_map[user.id]
        entry["total_shifts"] += 1
        
        # Night Shift Logic
        is_night = False
        if shift_type.shift_category == "night":
            is_night = True
        elif shift_type.name and ("夜" in shift_type.name or "Night" in shift_type.name):
            is_night = True
            
        if is_night:
            entry["night_shifts"] += 1
            
        # Weekend Logic
        if schedule.date.weekday() >= 5:
            entry["weekend_shifts"] += 1
            
        # Holiday Logic
        if is_holiday(schedule.date):
            entry["holiday_shifts"] += 1
            
    return list(stats_map.values())
