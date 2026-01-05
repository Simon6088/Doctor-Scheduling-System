import sys
sys.path.append('.')

from app.database import SessionLocal
from app.models import User, RoleEnum
from app.core.security import get_password_hash

db = SessionLocal()

try:
    # 创建用户 hjz
    existing = db.query(User).filter(User.username == "hjz").first()
    if existing:
        print("用户 hjz 已存在，重置密码...")
        existing.hashed_password = get_password_hash("hjz123")
        db.commit()
        print("✅ 密码已重置为 hjz123")
    else:
        print("创建用户 hjz...")
        user = User(
            username="hjz",
            hashed_password=get_password_hash("hjz123"),
            full_name="黄建忠",
            role=RoleEnum.DOCTOR,
            title="主治医师"
        )
        db.add(user)
        db.commit()
        print("✅ 用户创建成功")
        print(f"   用户名: hjz")
        print(f"   密码: hjz123")
        print(f"   角色: doctor")
        
except Exception as e:
    print(f"❌ 错误: {e}")
    import traceback
    traceback.print_exc()
finally:
    db.close()
