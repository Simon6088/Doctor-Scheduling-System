from pydantic import BaseModel, ConfigDict
from typing import Optional, List
from datetime import datetime
from enum import Enum

class RoleEnum(str, Enum):
    ADMIN = "admin"
    DOCTOR = "doctor"
    DEPARTMENT_MANAGER = "manager"

# Token Schemas
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None

# User Schemas
class UserBase(BaseModel):
    username: str
    full_name: Optional[str] = None
    role: RoleEnum = RoleEnum.DOCTOR
    department_id: Optional[int] = None
    title: Optional[str] = None
    phone: Optional[str] = None

class UserCreate(UserBase):
    password: str

class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    password: Optional[str] = None
    phone: Optional[str] = None

# Tag Schemas
class TagBase(BaseModel):
    name: str
    color: Optional[str] = "#1890ff"

class TagCreate(TagBase):
    pass

class Tag(TagBase):
    id: int
    model_config = ConfigDict(from_attributes=True)

class User(UserBase):
    id: int
    tags: List[Tag] = []
    
    model_config = ConfigDict(from_attributes=True)

# Department Schemas
class DepartmentBase(BaseModel):
    name: str
    parent_id: Optional[int] = None

class DepartmentCreate(DepartmentBase):
    pass

class Department(DepartmentBase):
    id: int
    children: List['Department'] = []
    
    model_config = ConfigDict(from_attributes=True)

# Room schemas
class RoomBase(BaseModel):
    name: str
    room_number: str
    department_id: Optional[int] = None
    capacity: int = 1
    description: Optional[str] = None

class RoomCreate(RoomBase):
    pass

class RoomUpdate(BaseModel):
    name: Optional[str] = None
    room_number: Optional[str] = None
    department_id: Optional[int] = None
    capacity: Optional[int] = None
    description: Optional[str] = None

class RoomResponse(RoomBase):
    id: int
    model_config = ConfigDict(from_attributes=True)

from datetime import date as date_type

class ShiftTypeBase(BaseModel):
    name: str
    start_time: str
    end_time: str
    score_weight: float = 1.0
    required_qualification: Optional[str] = None
    shift_category: str = "day"
    description: Optional[str] = None

class ShiftTypeCreate(ShiftTypeBase):
    pass

class ShiftTypeUpdate(BaseModel):
    name: Optional[str] = None
    start_time: Optional[str] = None
    end_time: Optional[str] = None
    score_weight: Optional[float] = None
    required_qualification: Optional[str] = None
    shift_category: Optional[str] = None
    description: Optional[str] = None

class ShiftTypeSchema(ShiftTypeBase):
    id: int

    model_config = {"from_attributes": True}

class ScheduleSchema(BaseModel):
    id: int
    date: date_type
    doctor_id: int
    shift_type_id: int
    room_id: Optional[int] = None
    status: str
    
    model_config = ConfigDict(from_attributes=True)

class TradeCreate(BaseModel):
    request_shift_id: int
    target_doctor_id: int
    reason: Optional[str] = None

class TradeResponse(BaseModel):
    id: int
    requester_id: int
    request_shift_id: int
    target_doctor_id: int
    status: str
    reason: Optional[str]
    
    model_config = {"from_attributes": True}

class TradeRespond(BaseModel):
    action: str # accept / reject

# Preference Schemas
class PreferenceBase(BaseModel):
    date: date_type
    type: str # desire / avoid
    shift_type_id: Optional[int] = None
    reason: Optional[str] = None

class PreferenceCreate(PreferenceBase):
    pass

class PreferenceResponse(PreferenceBase):
    id: int
    user_id: int
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)

# Notification Schemas
class NotificationBase(BaseModel):
    content: str
    type: str

class NotificationCreate(NotificationBase):
    user_id: int

class NotificationResponse(NotificationBase):
    id: int
    user_id: int
    is_read: bool = False
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)

# Feedback Schemas
class FeedbackCreate(BaseModel):
    type: str # review, bug, suggestion
    urgency: str = "low"
    content: str
    page: Optional[str] = None

class FeedbackResponse(FeedbackCreate):
    id: int
    user_id: int
    status: str
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)

# AuditLog Schemas
class AuditLog(BaseModel):
    id: int
    user_id: Optional[int]
    action: str
    resource: str
    resource_id: Optional[str] = None
    details: Optional[str] = None
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)
