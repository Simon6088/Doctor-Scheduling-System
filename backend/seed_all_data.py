"""
统一数据初始化脚本 - 用于 Docker 部署后初始化演示数据
执行顺序: 管理员 -> 基础数据 -> 60个医生 -> 诊室
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.database import SessionLocal, engine
from app import models
from app.core.security import get_password_hash
import random

def run_all():
    # 确保表已创建
    models.Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()
    
    try:
        print("=" * 50)
        print("🚀 开始初始化数据...")
        print("=" * 50)
        
        # ========== 1. 创建管理员 ==========
        print("\n[1/5] 创建管理员...")
        admin = db.query(models.User).filter(models.User.username == "admin").first()
        if not admin:
            admin = models.User(
                username="admin",
                hashed_password=get_password_hash("admin123"),
                full_name="Administrator",
                role=models.RoleEnum.ADMIN
            )
            db.add(admin)
            db.commit()
            print("  ✓ 管理员创建成功")
        else:
            admin.hashed_password = get_password_hash("admin123")
            db.commit()
            print("  - 管理员已存在，密码已重置")
        
        # ========== 2. 创建班次类型 ==========
        print("\n[2/5] 创建班次类型...")
        shift_types = [
            {"name": "白班", "start_time": "08:00", "end_time": "17:00", "weight": 1, "shift_category": "day"},
            {"name": "夜班", "start_time": "17:00", "end_time": "08:00", "weight": 2, "shift_category": "night"},
        ]
        for st_data in shift_types:
            existing = db.query(models.ShiftType).filter(models.ShiftType.name == st_data["name"]).first()
            if not existing:
                db.add(models.ShiftType(**st_data))
                print(f"  ✓ {st_data['name']}")
            else:
                print(f"  - {st_data['name']} 已存在")
        db.commit()
        
        # ========== 3. 创建科室 ==========
        print("\n[3/5] 创建科室...")
        departments = ["内科", "外科", "急诊科", "儿科", "妇产科"]
        dept_ids = {}
        for name in departments:
            existing = db.query(models.Department).filter(models.Department.name == name).first()
            if not existing:
                dept = models.Department(name=name)
                db.add(dept)
                db.commit()
                db.refresh(dept)
                dept_ids[name] = dept.id
                print(f"  ✓ {name}")
            else:
                dept_ids[name] = existing.id
                print(f"  - {name} 已存在")
        
        # ========== 4. 创建医生 (60个) ==========
        print("\n[4/5] 创建医生...")
        surnames = ["王", "李", "张", "刘", "陈", "杨", "赵", "黄", "周", "吴"]
        given_names = ["伟", "芳", "娜", "敏", "静", "丽", "强", "磊", "军", "杰"]
        titles = ["住院医师", "主治医师", "副主任医师", "主任医师"]
        
        existing_count = db.query(models.User).filter(models.User.role == models.RoleEnum.DOCTOR).count()
        to_create = max(0, 60 - existing_count)
        
        if to_create > 0:
            dept_id_list = list(dept_ids.values()) or [1]
            for i in range(to_create):
                username = f"doctor{existing_count + i + 1}"
                if db.query(models.User).filter(models.User.username == username).first():
                    continue
                doctor = models.User(
                    username=username,
                    hashed_password=get_password_hash("doctor123"),
                    full_name=f"{random.choice(surnames)}{random.choice(given_names)}{existing_count + i + 1}",
                    role=models.RoleEnum.DOCTOR,
                    department_id=random.choice(dept_id_list),
                    title=random.choice(titles),
                    phone=f"138{random.randint(10000000, 99999999)}"
                )
                db.add(doctor)
            db.commit()
            print(f"  ✓ 创建了 {to_create} 个医生")
        else:
            print(f"  - 已有 {existing_count} 个医生")
        
        # ========== 5. 创建诊室 ==========
        print("\n[5/5] 创建诊室...")
        rooms = [
            {"name": "诊室A101", "room_number": "A101", "capacity": 1},
            {"name": "诊室A102", "room_number": "A102", "capacity": 1},
            {"name": "诊室B201", "room_number": "B201", "capacity": 2},
            {"name": "诊室B202", "room_number": "B202", "capacity": 2},
            {"name": "急诊室", "room_number": "ER01", "capacity": 3},
        ]
        for room_data in rooms:
            existing = db.query(models.Room).filter(models.Room.room_number == room_data["room_number"]).first()
            if not existing:
                first_dept = db.query(models.Department).first()
                room_data["department_id"] = first_dept.id if first_dept else None
                db.add(models.Room(**room_data))
                print(f"  ✓ {room_data['name']}")
            else:
                print(f"  - {room_data['name']} 已存在")
        db.commit()
        
        print("\n" + "=" * 50)
        print("✅ 数据初始化完成！")
        print("=" * 50)
        print("\n📋 可用账号:")
        print("  管理员: admin / admin123")
        print("  医生: doctor1~doctor60 / doctor123")
        print("=" * 50)
        
    except Exception as e:
        print(f"\n❌ 错误: {e}")
        db.rollback()
        raise
    finally:
        db.close()

if __name__ == "__main__":
    run_all()
