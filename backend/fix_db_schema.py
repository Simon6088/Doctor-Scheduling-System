import sys
import os
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from app.database import Base, engine # Assuming these are available
from app import models

# Try to connect and select from schedules to see if room_id exists
try:
    with engine.connect() as connection:
        # Check columns of schedules table
        # For SQLite:
        if 'sqlite' in str(engine.url):
            result = connection.execute(text("PRAGMA table_info(schedules)"))
            columns = [row[1] for row in result]
            print(f"Columns in schedules table: {columns}")
            if 'room_id' not in columns:
                print("room_id column is MISSING!")
                # Try to add it
                print("Attempting to add room_id column...")
                connection.execute(text("ALTER TABLE schedules ADD COLUMN room_id INTEGER REFERENCES rooms(id)"))
                connection.commit()
                print("Added room_id column successfully.")
            else:
                print("room_id column exists.")
        
        # For PostgreSQL
        elif 'postgresql' in str(engine.url):
            print("Detected PostgreSQL database.")
            # Check if column exists
            result = connection.execute(text(
                "SELECT column_name FROM information_schema.columns WHERE table_name='schedules' AND column_name='room_id'"
            ))
            if result.rowcount == 0:
                print("room_id column is MISSING in schedules table!")
                print("Attempting to add room_id column...")
                connection.execute(text("ALTER TABLE schedules ADD COLUMN room_id INTEGER REFERENCES rooms(id)"))
                connection.commit()
                print("Added room_id column successfully.")
            else:
                print("room_id column exists in schedules table.")
            
except Exception as e:
    print(f"Error checking/migrating database: {e}")
    import traceback
    traceback.print_exc()
