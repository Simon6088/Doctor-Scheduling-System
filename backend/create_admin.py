import sys
import os

# Add current directory to path so we can import app
sys.path.append(os.getcwd())

from app.database import SessionLocal
from app.models import User, RoleEnum
from app.core.security import get_password_hash

def create_admin():
    db = SessionLocal()
    try:
        # Check if exists
        user = db.query(User).filter(User.username == "admin").first()
        if user:
            print("Admin user already exists.")
            # Update password just in case? No, let's just leave it if exists or maybe reset?
            # User asked to create it, implyin it might not exist or they want that specific pass.
            # Let's update password to be sure it's admin123
            user.hashed_password = get_password_hash("admin123")
            db.commit()
            print("Admin user password reset to admin123.")
            return

        hashed_password = get_password_hash("admin123")
        admin_user = User(
            username="admin",
            hashed_password=hashed_password,
            full_name="Administrator",
            role=RoleEnum.ADMIN
        )
        db.add(admin_user)
        db.commit()
        print("Admin user created successfully.")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    create_admin()
