"""
创建60个虚拟医生用于测试排班
"""
from app.database import get_db
from app import models
from app.core.security import get_password_hash
import random

def create_60_doctors():
    db = next(get_db())
    
    print("开始创建60个虚拟医生...")
    
    # 获取科室ID
    departments = db.query(models.Department).all()
    dept_ids = [d.id for d in departments]
    
    if not dept_ids:
        print("错误：没有科室数据")
        return
    
    # 姓氏和名字
    surnames = ["王", "李", "张", "刘", "陈", "杨", "赵", "黄", "周", "吴", 
                "徐", "孙", "胡", "朱", "高", "林", "何", "郭", "马", "罗",
                "梁", "宋", "郑", "谢", "韩", "唐", "冯", "于", "董", "萧"]
    
    given_names = ["伟", "芳", "娜", "秀英", "敏", "静", "丽", "强", "磊", "军",
                   "洋", "勇", "艳", "杰", "涛", "明", "超", "秀兰", "霞", "平",
                   "刚", "桂英", "建华", "文", "辉", "力", "华", "鹏", "玲", "飞"]
    
    titles = ["住院医师", "主治医师", "副主任医师", "主任医师"]
    
    # 检查已有医生数量
    existing_count = db.query(models.User).filter(models.User.role == "doctor").count()
    print(f"当前医生数量: {existing_count}")
    
    # 需要创建的数量
    to_create = 60 - existing_count
    
    if to_create <= 0:
        print(f"已有{existing_count}个医生，无需创建更多")
        return
    
    print(f"需要创建 {to_create} 个医生")
    
    created = 0
    for i in range(to_create):
        # 生成姓名
        surname = random.choice(surnames)
        given_name = random.choice(given_names)
        full_name = f"{surname}{given_name}{i+1}"
        
        # 生成用户名
        username = f"doctor{existing_count + i + 1}"
        
        # 检查用户名是否存在
        existing = db.query(models.User).filter(models.User.username == username).first()
        if existing:
            continue
        
        # 随机分配科室和职称
        dept_id = random.choice(dept_ids)
        title = random.choice(titles)
        
        # 创建医生
        doctor = models.User(
            username=username,
            hashed_password=get_password_hash("doctor123"),
            full_name=full_name,
            role="doctor",
            department_id=dept_id,
            title=title,
            phone=f"138{random.randint(10000000, 99999999)}"
        )
        
        db.add(doctor)
        created += 1
        
        if (created) % 10 == 0:
            print(f"  已创建 {created} 个医生...")
    
    db.commit()
    
    # 验证
    total = db.query(models.User).filter(models.User.role == "doctor").count()
    print(f"\n✅ 完成！当前医生总数: {total}")
    print(f"所有医生的密码都是: doctor123")

if __name__ == "__main__":
    create_60_doctors()
