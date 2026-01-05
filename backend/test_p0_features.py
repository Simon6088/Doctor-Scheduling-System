"""
P0功能测试脚本
测试所有新开发的P0高优先级功能
"""
import requests
import json
from datetime import datetime, timedelta

BASE_URL = "http://127.0.0.1:8000"

# 测试结果
test_results = []

def log_test(test_name, success, message=""):
    status = "✅ PASS" if success else "❌ FAIL"
    test_results.append(f"{status} - {test_name}: {message}")
    print(f"{status} - {test_name}: {message}")

def login(username, password):
    """登录并获取token"""
    response = requests.post(
        f"{BASE_URL}/token",
        data={"username": username, "password": password}
    )
    if response.status_code == 200:
        return response.json()["access_token"]
    return None

def test_shift_types(token):
    """测试班次管理功能"""
    headers = {"Authorization": f"Bearer {token}"}
    
    print("\n=== 测试班次管理 ===")
    
    # 1. 创建班次
    shift_data = {
        "name": "测试白班",
        "start_time": "08:00",
        "end_time": "17:00",
        "weight": 1.0,
        "shift_category": "day",
        "description": "测试用白班"
    }
    response = requests.post(f"{BASE_URL}/shift-types/", json=shift_data, headers=headers)
    if response.status_code == 200:
        shift_id = response.json()["id"]
        log_test("创建班次", True, f"ID: {shift_id}")
    else:
        log_test("创建班次", False, f"状态码: {response.status_code}")
        return
    
    # 2. 获取班次列表
    response = requests.get(f"{BASE_URL}/shift-types/", headers=headers)
    if response.status_code == 200:
        shifts = response.json()
        log_test("获取班次列表", True, f"共 {len(shifts)} 个班次")
    else:
        log_test("获取班次列表", False)
    
    # 3. 更新班次
    update_data = {"description": "更新后的描述"}
    response = requests.put(f"{BASE_URL}/shift-types/{shift_id}", json=update_data, headers=headers)
    log_test("更新班次", response.status_code == 200)
    
    # 4. 删除班次
    response = requests.delete(f"{BASE_URL}/shift-types/{shift_id}", headers=headers)
    log_test("删除班次", response.status_code == 200)

def test_schedules(token):
    """测试排班功能"""
    headers = {"Authorization": f"Bearer {token}"}
    
    print("\n=== 测试排班功能 ===")
    
    # 1. 生成排班
    today = datetime.now().strftime("%Y-%m-%d")
    response = requests.post(
        f"{BASE_URL}/schedules/generate?start_date={today}&days=7",
        headers=headers
    )
    log_test("生成排班", response.status_code == 200, f"生成7天排班")
    
    # 2. 获取排班列表
    response = requests.get(f"{BASE_URL}/schedules/", headers=headers)
    if response.status_code == 200:
        schedules = response.json()
        log_test("获取排班列表", True, f"共 {len(schedules)} 条排班")
        
        # 3. 按日期筛选
        tomorrow = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")
        response = requests.get(
            f"{BASE_URL}/schedules/?start_date={tomorrow}&end_date={tomorrow}",
            headers=headers
        )
        if response.status_code == 200:
            filtered = response.json()
            log_test("按日期筛选排班", True, f"筛选出 {len(filtered)} 条")
        else:
            log_test("按日期筛选排班", False)
    else:
        log_test("获取排班列表", False)

def test_trades(token):
    """测试换班审批功能"""
    headers = {"Authorization": f"Bearer {token}"}
    
    print("\n=== 测试换班审批 ===")
    
    # 1. 获取所有换班请求
    response = requests.get(f"{BASE_URL}/trades/", headers=headers)
    if response.status_code == 200:
        trades = response.json()
        log_test("获取换班请求列表", True, f"共 {len(trades)} 个请求")
        
        # 2. 测试审批功能（如果有待审批的请求）
        pending_trades = [t for t in trades if t["status"] == "pending"]
        if pending_trades:
            trade_id = pending_trades[0]["id"]
            
            # 批准
            response = requests.put(
                f"{BASE_URL}/trades/{trade_id}/respond",
                json={"action": "approved"},
                headers=headers
            )
            log_test("批准换班请求", response.status_code == 200)
        else:
            log_test("批准换班请求", True, "无待审批请求，跳过")
    else:
        log_test("获取换班请求列表", False)
    
    # 3. 获取收到的换班请求
    response = requests.get(f"{BASE_URL}/trades/incoming", headers=headers)
    if response.status_code == 200:
        incoming = response.json()
        log_test("获取收到的换班请求", True, f"共 {len(incoming)} 个")
    else:
        log_test("获取收到的换班请求", False)

def test_users_and_departments(token):
    """测试用户和科室功能"""
    headers = {"Authorization": f"Bearer {token}"}
    
    print("\n=== 测试用户和科室 ===")
    
    # 1. 获取用户列表
    response = requests.get(f"{BASE_URL}/users/", headers=headers)
    if response.status_code == 200:
        users = response.json()
        log_test("获取用户列表", True, f"共 {len(users)} 个用户")
    else:
        log_test("获取用户列表", False)
    
    # 2. 获取当前用户信息
    response = requests.get(f"{BASE_URL}/users/me", headers=headers)
    if response.status_code == 200:
        me = response.json()
        log_test("获取当前用户信息", True, f"用户: {me.get('full_name')}")
    else:
        log_test("获取当前用户信息", False)
    
    # 3. 获取科室列表
    response = requests.get(f"{BASE_URL}/departments/", headers=headers)
    if response.status_code == 200:
        departments = response.json()
        log_test("获取科室列表", True, f"共 {len(departments)} 个科室")
    else:
        log_test("获取科室列表", False)

def main():
    print("=" * 60)
    print("P0功能测试开始")
    print("=" * 60)
    
    # 1. 测试管理员登录
    print("\n=== 测试管理员登录 ===")
    admin_token = login("admin", "admin123")
    if admin_token:
        log_test("管理员登录", True)
    else:
        log_test("管理员登录", False, "无法继续测试")
        return
    
    # 2. 测试医生登录
    print("\n=== 测试医生登录 ===")
    doctor_token = login("hjz", "hjz123")
    if doctor_token:
        log_test("医生登录", True)
    else:
        log_test("医生登录", False)
    
    # 3. 使用管理员token测试各项功能
    test_shift_types(admin_token)
    test_schedules(admin_token)
    test_trades(admin_token)
    test_users_and_departments(admin_token)
    
    # 4. 测试医生权限（使用医生token）
    if doctor_token:
        print("\n=== 测试医生权限 ===")
        headers = {"Authorization": f"Bearer {doctor_token}"}
        
        # 医生应该能查看排班
        response = requests.get(f"{BASE_URL}/schedules/", headers=headers)
        log_test("医生查看排班", response.status_code == 200)
        
        # 医生应该能查看自己的信息
        response = requests.get(f"{BASE_URL}/users/me", headers=headers)
        log_test("医生查看个人信息", response.status_code == 200)
    
    # 5. 打印测试总结
    print("\n" + "=" * 60)
    print("测试总结")
    print("=" * 60)
    
    passed = sum(1 for r in test_results if "✅" in r)
    failed = sum(1 for r in test_results if "❌" in r)
    total = len(test_results)
    
    print(f"\n总测试数: {total}")
    print(f"通过: {passed} ✅")
    print(f"失败: {failed} ❌")
    print(f"通过率: {passed/total*100:.1f}%")
    
    print("\n详细结果:")
    for result in test_results:
        print(result)
    
    print("\n" + "=" * 60)
    print("测试完成")
    print("=" * 60)

if __name__ == "__main__":
    main()
