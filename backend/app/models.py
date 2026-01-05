from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, DateTime, Date, Enum as SAEnum, Table
from sqlalchemy.orm import relationship
from .database import Base
import enum
from datetime import datetime

class RoleEnum(str, enum.Enum):
    ADMIN = "admin"
    DOCTOR = "doctor"
    DEPARTMENT_MANAGER = "manager"

# Association Table for Many-to-Many
user_tags = Table('user_tags', Base.metadata,
    Column('user_id', Integer, ForeignKey('users.id')),
    Column('tag_id', Integer, ForeignKey('tags.id'))
)

class Tag(Base):
    __tablename__ = "tags"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    color = Column(String, default="#1890ff")

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    full_name = Column(String)
    role = Column(SAEnum(RoleEnum), default=RoleEnum.DOCTOR)
    department_id = Column(Integer, ForeignKey("departments.id"))
    title = Column(String) 
    phone = Column(String)
    
    department = relationship("Department", back_populates="users")
    schedules = relationship("Schedule", back_populates="doctor")
    preferences = relationship("Preference", back_populates="user")
    tags = relationship("Tag", secondary=user_tags, backref="users")

class Department(Base):
    __tablename__ = "departments"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    parent_id = Column(Integer, ForeignKey("departments.id"), nullable=True)
    
    users = relationship("User", back_populates="department")
    rooms = relationship("Room", back_populates="department")
    children = relationship("Department")

class Room(Base):
    __tablename__ = "rooms"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    room_number = Column(String, unique=True, index=True)
    department_id = Column(Integer, ForeignKey("departments.id"), nullable=True)
    capacity = Column(Integer, default=1)
    description = Column(String, nullable=True)
    
    department = relationship("Department", back_populates="rooms")
    schedules = relationship("Schedule", back_populates="room")

class ShiftType(Base):
    __tablename__ = "shift_types"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String) # e.g. Day, Night
    start_time = Column(String) # "08:00"
    end_time = Column(String) # "17:00"
    weight = Column(Integer, default=1)
    required_qualification = Column(String, nullable=True)
    shift_category = Column(String, default="day")  # day/night/oncall/backup/holiday
    description = Column(String, nullable=True)

class Schedule(Base):
    __tablename__ = "schedules"
    
    id = Column(Integer, primary_key=True, index=True)
    doctor_id = Column(Integer, ForeignKey("users.id"))
    shift_type_id = Column(Integer, ForeignKey("shift_types.id"))
    room_id = Column(Integer, ForeignKey("rooms.id"), nullable=True)
    date = Column(Date, index=True)
    status = Column(String, default="draft")
    
    doctor = relationship("User", back_populates="schedules")
    shift_type = relationship("ShiftType")
    room = relationship("Room", back_populates="schedules")

class TradeStatus(str, enum.Enum):
    PENDING = "pending"
    ACCEPTED = "accepted"
    REJECTED = "rejected"
    APPROVED = "approved" # Admin final approval
    CANCELLED = "cancelled"

class ShiftTrade(Base):
    __tablename__ = "shift_trades"
    
    id = Column(Integer, primary_key=True, index=True)
    requester_id = Column(Integer, ForeignKey("users.id"))
    request_shift_id = Column(Integer, ForeignKey("schedules.id"))
    
    target_doctor_id = Column(Integer, ForeignKey("users.id"))
    # In PRD: "Select my shift" -> "Select target doctor". 
    # Usually implies swapping for *one of their shifts* or just giving away?
    # PRD 3.2.2: "Initiate Trade: Select Own Shift -> Select Target Doctor -> Submit".
    # And "Select Target Shift" implied? Usually swaps are 1-for-1. 
    # Let's assume for MVP it's a request to *give* a shift or *swap*. 
    # We'll enable specific target shift_id to be nullable (general request) or specific.
    # But usually you swap with a specific date. 
    # Let's stick to: Requester Shift <-> Target Doctor (and optionally Target Shift).
    
    status = Column(String, default=TradeStatus.PENDING)
    reason = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    requester = relationship("User", foreign_keys=[requester_id])
    target_doctor = relationship("User", foreign_keys=[target_doctor_id])
    request_shift = relationship("Schedule", foreign_keys=[request_shift_id])


class PreferenceType(str, enum.Enum):
    DESIRE = "desire"   # 希望上班
    AVOID = "avoid"     # 不希望上班

class Preference(Base):
    __tablename__ = "preferences"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    date = Column(Date, index=True)
    type = Column(String, default=PreferenceType.AVOID) # desire / avoid
    shift_type_id = Column(Integer, ForeignKey("shift_types.id"), nullable=True) # If null, applies to all shifts on that day
    reason = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    user = relationship("User", back_populates="preferences")
    shift_type = relationship("ShiftType")

class NotificationType(str, enum.Enum):
    TRADE_REQUEST = "trade_request" # Someone wants to trade with you
    TRADE_RESULT = "trade_result"   # Your trade was approved/rejected
    SYSTEM = "system"               # General system message

class Notification(Base):
    __tablename__ = "notifications"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    content = Column(String)
    is_read = Column(Boolean, default=False)
    type = Column(String, default=NotificationType.SYSTEM)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    user = relationship("User", back_populates="notifications")

# Add relationships to User model
User.notifications = relationship("Notification", back_populates="user")

class FeedbackType(str, enum.Enum):
    REVIEW = "review"
    BUG = "bug"
    SUGGESTION = "suggestion"

class UrgencyLevel(str, enum.Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"

class Feedback(Base):
    __tablename__ = "feedbacks"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    type = Column(String) # FeedbackType
    urgency = Column(String, default=UrgencyLevel.LOW)
    content = Column(String)
    page = Column(String, nullable=True)
    status = Column(String, default="open") # open, closed
    created_at = Column(DateTime, default=datetime.utcnow)
    
    user = relationship("User", back_populates="feedbacks")

User.feedbacks = relationship("Feedback", back_populates="user")

class AuditLog(Base):
    __tablename__ = "audit_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    action = Column(String) # CREATE, UPDATE, DELETE, APPROVE, REJECT
    resource = Column(String) # schedule, trade, user
    resource_id = Column(String, nullable=True)
    details = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    user = relationship("User")

