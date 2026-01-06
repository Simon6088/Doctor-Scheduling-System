import os
import urllib.parse
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# PostgreSQL connection
# Prioritize environment variable (Render/Supabase), fallback to localhost
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:dev123@localhost:5432/postgres")

# Fix Render/Heroku postgres:// schema for SQLAlchemy
if DATABASE_URL and DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

# DEBUG: Print user and host to logs to diagnose Render connection issues
try:
    # Use generic parsing to avoid exposing password if possible, or just extract specific parts
    # SQLAlchemy URL format might need specific parsing, but urlparse works for standard schemes
    # Handle the postgresql scheme
    temp_url = DATABASE_URL.replace("postgresql+psycopg2://", "postgresql://")
    url_parts = urllib.parse.urlparse(temp_url)
    print(f"DEBUG_DB_CONFIG: User={url_parts.username}, Host={url_parts.hostname}, Port={url_parts.port}, Scheme={url_parts.scheme}")
except Exception as e:
    print(f"DEBUG_DB_CONFIG Error: {e}")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
