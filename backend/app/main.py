from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text
from sqlalchemy.orm import Session
from .database import engine, Base, get_db
from . import models
from .api import auth, users, departments, schedules, trades, shift_types, rooms, preferences, stats, notifications, feedback, tags, audit

# Create tables
models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Doctor Scheduling System API")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:5174", "http://localhost:5175", "http://127.0.0.1:5173", "http://127.0.0.1:5174", "http://127.0.0.1:5175", "*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, tags=["auth"])
app.include_router(users.router, tags=["users"])
app.include_router(departments.router, tags=["departments"])
app.include_router(schedules.router, tags=["schedules"])
app.include_router(trades.router, tags=["trades"])
app.include_router(shift_types.router, tags=["shift-types"])
app.include_router(rooms.router, tags=["rooms"])
app.include_router(preferences.router, tags=["preferences"])
app.include_router(stats.router, tags=["stats"])
app.include_router(notifications.router)
app.include_router(feedback.router)
app.include_router(tags.router)
app.include_router(audit.router)

@app.get("/")
def read_root():
    return {"message": "Doctor Scheduling System API is running"}

@app.get("/health/db")
def check_db(db: Session = Depends(get_db)):
    try:
        result = db.execute(text("SELECT 1"))
        return {"status": "ok", "result": result.scalar()}
    except Exception as e:
        return {"status": "error", "message": str(e)}
