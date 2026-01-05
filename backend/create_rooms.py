"""
创建20个虚拟诊室
"""
from app.database import get_db
from app import models

def create_rooms():
    db = next(get_db())
    
    print("开始创建20个虚拟诊室...")
    
    # 获取科室
    departments = db.query(models.Department).all()
    dept_ids = [d.id for d in departments] if departments else [None]
    
    rooms_data = []
    for i in range(1, 21):
        room_number = f"R{i:03d}"  # R001, R002, ...
        name = f"诊室{i}号"
        
        # 循环分配科室
        dept_id = dept_ids[(i-1) % len(dept_ids)] if dept_ids[0] is not None else None
        
        rooms_data.append({
            "name": name,
            "room_number": room_number,
            "department_id": dept_id,
            "capacity": 1,
            "description": f"标准诊室，可容纳1名医生"
        })
    
    # 检查并创建
    created = 0
    for room_data in rooms_data:
        existing = db.query(models.Room).filter(
            models.Room.room_number == room_data["room_number"]
        ).first()
        
        if not existing:
            room = models.Room(**room_data)
            db.add(room)
            created += 1
            if created % 5 == 0:
                print(f"  已创建 {created} 个诊室...")
    
    db.commit()
    
    # 验证
    total = db.query(models.Room).count()
    print(f"\n✅ 完成！当前诊室总数: {total}")
    
    # 显示诊室列表
    print("\n诊室列表:")
    rooms = db.query(models.Room).all()
    for room in rooms[:10]:  # 只显示前10个
        dept_name = "未分配"
        if room.department_id:
            dept = db.query(models.Department).filter(models.Department.id == room.department_id).first()
            dept_name = dept.name if dept else "未知"
        print(f"  {room.room_number} - {room.name} (科室: {dept_name})")
    if len(rooms) > 10:
        print(f"  ... 还有 {len(rooms) - 10} 个诊室")

if __name__ == "__main__":
    create_rooms()
