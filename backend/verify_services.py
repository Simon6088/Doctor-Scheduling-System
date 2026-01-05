import requests
import time

BASE_URL = "http://127.0.0.1:8000"

print("等待后端启动...")
time.sleep(3)

print("\n=== 测试后端服务 ===")

# 1. 测试健康检查
print("\n1. 健康检查...")
try:
    resp = requests.get(f"{BASE_URL}/health/db", timeout=5)
    if resp.status_code == 200:
        print("✅ 后端服务正常")
    else:
        print(f"❌ 健康检查失败: {resp.status_code}")
except Exception as e:
    print(f"❌ 无法连接到后端: {e}")
    exit(1)

# 2. 测试管理员登录
print("\n2. 测试管理员登录...")
try:
    resp = requests.post(f"{BASE_URL}/token", data={
        "username": "admin",
        "password": "admin123"
    })
    if resp.status_code == 200:
        admin_token = resp.json()["access_token"]
        print("✅ 管理员登录成功")
    else:
        print(f"❌ 管理员登录失败: {resp.text}")
        exit(1)
except Exception as e:
    print(f"❌ 登录请求失败: {e}")
    exit(1)

# 3. 测试hjz用户登录
print("\n3. 测试hjz用户登录...")
try:
    resp = requests.post(f"{BASE_URL}/token", data={
        "username": "hjz",
        "password": "hjz123"
    })
    if resp.status_code == 200:
        hjz_token = resp.json()["access_token"]
        print("✅ hjz用户登录成功")
    else:
        print(f"❌ hjz登录失败: {resp.text}")
except Exception as e:
    print(f"❌ hjz登录请求失败: {e}")

# 4. 测试获取排班（修复后）
print("\n4. 测试获取排班...")
try:
    headers = {"Authorization": f"Bearer {admin_token}"}
    resp = requests.get(f"{BASE_URL}/schedules/", headers=headers)
    if resp.status_code == 200:
        schedules = resp.json()
        print(f"✅ 获取排班成功，共 {len(schedules)} 条记录")
        if schedules:
            print(f"   示例: 日期={schedules[0]['date']}, 医生ID={schedules[0]['doctor_id']}")
    else:
        print(f"❌ 获取排班失败: {resp.status_code} - {resp.text}")
except Exception as e:
    print(f"❌ 获取排班请求失败: {e}")

# 5. 测试获取用户信息
print("\n5. 测试获取hjz用户信息...")
try:
    headers = {"Authorization": f"Bearer {hjz_token}"}
    resp = requests.get(f"{BASE_URL}/users/me", headers=headers)
    if resp.status_code == 200:
        user = resp.json()
        print(f"✅ 获取用户信息成功")
        print(f"   姓名: {user.get('full_name')}")
        print(f"   角色: {user.get('role')}")
    else:
        print(f"❌ 获取用户信息失败: {resp.text}")
except Exception as e:
    print(f"❌ 获取用户信息失败: {e}")

print("\n" + "="*50)
print("测试完成！")
print("="*50)
print("\n前端服务:")
print("  - 管理后台: http://localhost:5173")
print("  - 移动端H5: http://localhost:5174 (或 5183)")
print("\n登录信息:")
print("  - 管理员: admin / admin123")
print("  - 医生hjz: hjz / hjz123")
