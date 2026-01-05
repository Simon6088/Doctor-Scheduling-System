"""
初始化系统数据：创建班次类型、科室和医生
"""
from app.database import get_db
from app import models
from app.core.security import get_password_hash

def init_data():
    db = next(get_db())
    
    print("开始初始化数据...")
    
    # 1. 创建班次类型
    print("\n创建班次类型...")
    shift_types = [
        {
            "name": "白班",
            "start_time": "08:00",
            "end_time": "17:00",
            "weight": 1,
            "shift_category": "day",
            "description": "正常白班"
        },
        {
            "name": "夜班",
            "start_time": "17:00",
            "end_time": "08:00",
            "weight": 2,
            "shift_category": "night",
            "description": "夜间值班"
        }
    ]
    
    for st_data in shift_types:
        existing = db.query(models.ShiftType).filter(models.ShiftType.name == st_data["name"]).first()
        if not existing:
            shift_type = models.ShiftType(**st_data)
            db.add(shift_type)
            print(f"  ✓ 创建班次: {st_data['name']}")
        else:
            print(f"  - 班次已存在: {st_data['name']}")
    
    db.commit()
    
    # 2. 创建科室
    print("\n创建科室...")
    departments = [
        {"name": "内科"},
        {"name": "外科"},
        {"name": "急诊科"}
    ]
    
    dept_ids = {}
    for dept_data in departments:
        existing = db.query(models.Department).filter(models.Department.name == dept_data["name"]).first()
        if not existing:
            dept = models.Department(**dept_data)
            db.add(dept)
            db.commit()
            db.refresh(dept)
            dept_ids[dept_data["name"]] = dept.id
            print(f"  ✓ 创建科室: {dept_data['name']}")
        else:
            dept_ids[dept_data["name"]] = existing.id
            print(f"  - 科室已存在: {dept_data['name']}")
    
    # 3. 创建测试医生
    print("\n创建测试医生...")
    doctors = [
        {
            "username": "doctor1",
            "password": "doctor123",
            "full_name": "张医生",
            "role": "doctor",
            "department_id": dept_ids.get("内科", 1),
            "title": "主治医师"
        },
        {
            "username": "doctor2",
            "password": "doctor123",
            "full_name": "李医生",
            "role": "doctor",
            "department_id": dept_ids.get("内科", 1),
            "title": "住院医师"
        },
        {
            "username": "doctor3",
            "password": "doctor123",
            "full_name": "王医生",
            "role": "doctor",
            "department_id": dept_ids.get("外科", 2),
            "title": "主治医师"
        }
    ]
    
    for doc_data in doctors:
        existing = db.query(models.User).filter(models.User.username == doc_data["username"]).first()
        if not existing:
            password = doc_data.pop("password")
            doc_data["hashed_password"] = get_password_hash(password)
            doctor = models.User(**doc_data)
            db.add(doctor)
            db.commit()
            print(f"  ✓ 创建医生: {doc_data['full_name']} ({doc_data['username']})")
        else:
            print(f"  - 医生已存在: {existing.full_name}")
    
    print("\n✅ 数据初始化完成！")
    print("\n可用账号：")
    print("  管理员: admin / admin123")
    print("  医生: hjz / hjz123")
    print("  医生: doctor1 / doctor123")
    print("  医生: doctor2 / doctor123")
    print("  医生: doctor3 / doctor123")

if __name__ == "__main__":
    init_data()
