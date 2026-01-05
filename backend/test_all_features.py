import requests
import json

BASE_URL = "http://127.0.0.1:8000"

def test_all_features():
    print("=" * 60)
    print("开始测试医院排班系统各项功能")
    print("=" * 60)
    
    # 1. 登录获取 token
    print("\n1. 测试登录...")
    login_resp = requests.post(f"{BASE_URL}/token", data={
        "username": "admin",
        "password": "admin123"
    })
    if login_resp.status_code != 200:
        print(f"❌ 登录失败: {login_resp.text}")
        return
    
    token = login_resp.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    print("✅ 登录成功")
    
    # 2. 测试科室管理
    print("\n2. 测试科室管理...")
    
    # 创建科室
    dept_data = {"name": "内科", "parent_id": None}
    resp = requests.post(f"{BASE_URL}/departments/", json=dept_data, headers=headers)
    if resp.status_code == 200:
        dept_id = resp.json()["id"]
        print(f"✅ 创建科室成功 (ID: {dept_id})")
    else:
        print(f"❌ 创建科室失败: {resp.text}")
        dept_id = None
    
    # 查询科室
    resp = requests.get(f"{BASE_URL}/departments/", headers=headers)
    if resp.status_code == 200:
        depts = resp.json()
        print(f"✅ 查询科室成功，共 {len(depts)} 个科室")
    else:
        print(f"❌ 查询科室失败")
    
    # 更新科室
    if dept_id:
        update_data = {"name": "内科（更新）", "parent_id": None}
        resp = requests.put(f"{BASE_URL}/departments/{dept_id}", json=update_data, headers=headers)
        if resp.status_code == 200:
            print("✅ 更新科室成功")
        else:
            print(f"❌ 更新科室失败: {resp.text}")
    
    # 3. 测试医生管理
    print("\n3. 测试医生管理...")
    
    # 创建医生
    doctor_data = {
        "username": "doctor_test",
        "password": "test123",
        "full_name": "测试医生",
        "role": "doctor",
        "title": "主治医师",
        "phone": "13800138000"
    }
    resp = requests.post(f"{BASE_URL}/users/", json=doctor_data, headers=headers)
    if resp.status_code == 200:
        doctor_id = resp.json()["id"]
        print(f"✅ 创建医生成功 (ID: {doctor_id})")
    else:
        print(f"❌ 创建医生失败: {resp.text}")
        doctor_id = None
    
    # 查询医生
    resp = requests.get(f"{BASE_URL}/users/", headers=headers)
    if resp.status_code == 200:
        users = resp.json()
        print(f"✅ 查询医生成功，共 {len(users)} 个用户")
    else:
        print(f"❌ 查询医生失败")
    
    # 更新医生
    if doctor_id:
        update_data = {
            "full_name": "测试医生（更新）",
            "phone": "13900139000"
        }
        resp = requests.put(f"{BASE_URL}/users/{doctor_id}", json=update_data, headers=headers)
        if resp.status_code == 200:
            print("✅ 更新医生成功")
        else:
            print(f"❌ 更新医生失败: {resp.text}")
    
    # 4. 测试排班管理
    print("\n4. 测试排班管理...")
    
    # 生成排班
    resp = requests.post(f"{BASE_URL}/schedules/generate?start_date=2026-01-06&days=7", headers=headers)
    if resp.status_code == 200:
        schedules = resp.json()
        print(f"✅ 生成排班成功，共 {len(schedules)} 条记录")
        schedule_id = schedules[0]["id"] if schedules else None
    else:
        print(f"❌ 生成排班失败: {resp.text}")
        schedule_id = None
    
    # 查询排班
    resp = requests.get(f"{BASE_URL}/schedules/", headers=headers)
    if resp.status_code == 200:
        schedules = resp.json()
        print(f"✅ 查询排班成功，共 {len(schedules)} 条记录")
    else:
        print(f"❌ 查询排班失败")
    
    # 删除排班
    if schedule_id:
        resp = requests.delete(f"{BASE_URL}/schedules/{schedule_id}", headers=headers)
        if resp.status_code == 200:
            print("✅ 删除排班成功")
        else:
            print(f"❌ 删除排班失败: {resp.text}")
    
    # 5. 测试换班管理
    print("\n5. 测试换班管理...")
    
    # 查询当前医生的排班
    resp = requests.get(f"{BASE_URL}/schedules/", headers=headers)
    if resp.status_code == 200 and resp.json():
        my_shift = resp.json()[0]
        
        # 创建换班请求
        trade_data = {
            "request_shift_id": my_shift["id"],
            "target_doctor_id": doctor_id if doctor_id else 2,
            "reason": "测试换班"
        }
        resp = requests.post(f"{BASE_URL}/trades/", json=trade_data, headers=headers)
        if resp.status_code == 200:
            print("✅ 创建换班请求成功")
        else:
            print(f"❌ 创建换班请求失败: {resp.text}")
    else:
        print("⚠️  没有可用的排班记录，跳过换班测试")
    
    # 清理测试数据
    print("\n6. 清理测试数据...")
    if doctor_id:
        resp = requests.delete(f"{BASE_URL}/users/{doctor_id}", headers=headers)
        print("✅ 删除测试医生" if resp.status_code == 200 else "❌ 删除测试医生失败")
    
    if dept_id:
        resp = requests.delete(f"{BASE_URL}/departments/{dept_id}", headers=headers)
        print("✅ 删除测试科室" if resp.status_code == 200 else "❌ 删除测试科室失败")
    
    print("\n" + "=" * 60)
    print("测试完成！")
    print("=" * 60)

if __name__ == "__main__":
    test_all_features()
