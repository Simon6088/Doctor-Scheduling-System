import sys
sys.path.append('.')

from app.database import SessionLocal
from app.models import Schedule
from sqlalchemy import text

db = SessionLocal()

try:
    # 直接查询数据库
    print("直接查询数据库中的排班记录...")
    schedules = db.query(Schedule).all()
    print(f"找到 {len(schedules)} 条记录")
    
    for s in schedules[:5]:
        print(f"ID: {s.id}, Date: {s.date}, Doctor: {s.doctor_id}, Shift: {s.shift_type_id}, Status: {s.status}")
    
    # 测试序列化
    print("\n测试序列化...")
    from app.schemas import ScheduleSchema
    from pydantic import ValidationError
    
    for s in schedules[:3]:
        try:
            schema = ScheduleSchema.model_validate(s)
            print(f"✅ 序列化成功: {schema}")
        except ValidationError as e:
            print(f"❌ 序列化失败: {e}")
            print(f"   对象属性: date={s.date}, doctor_id={s.doctor_id}, shift_type_id={s.shift_type_id}")
            
except Exception as e:
    print(f"错误: {e}")
    import traceback
    traceback.print_exc()
finally:
    db.close()
