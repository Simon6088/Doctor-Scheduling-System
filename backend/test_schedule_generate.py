"""
测试排班生成API
"""
import requests
import json

BASE_URL = "http://127.0.0.1:8000"

# 1. 登录获取token
print("1. 登录...")
response = requests.post(
    f"{BASE_URL}/token",
    data={"username": "admin", "password": "admin123"}
)
if response.status_code == 200:
    token = response.json()["access_token"]
    print(f"✓ 登录成功，token: {token[:20]}...")
else:
    print(f"✗ 登录失败: {response.status_code}")
    exit(1)

headers = {"Authorization": f"Bearer {token}"}

# 2. 检查医生数量
print("\n2. 检查医生...")
response = requests.get(f"{BASE_URL}/users/", headers=headers)
users = response.json()
doctors = [u for u in users if u["role"] == "doctor"]
print(f"医生数量: {len(doctors)}")
for doc in doctors:
    print(f"  - {doc['full_name']} (ID: {doc['id']}, 科室: {doc.get('department_id', 'N/A')})")

# 3. 检查班次类型
print("\n3. 检查班次类型...")
response = requests.get(f"{BASE_URL}/shift-types/", headers=headers)
shift_types = response.json()
print(f"班次类型数量: {len(shift_types)}")
for st in shift_types:
    print(f"  - {st['name']} (ID: {st['id']})")

# 4. 尝试生成排班
print("\n4. 尝试生成排班...")
response = requests.post(
    f"{BASE_URL}/schedules/generate?start_date=2026-01-05&days=7",
    headers=headers
)
print(f"状态码: {response.status_code}")
print(f"响应: {response.text}")

if response.status_code == 200:
    print("✓ 排班生成成功！")
else:
    print(f"✗ 排班生成失败")
    try:
        error = response.json()
        print(f"错误详情: {json.dumps(error, indent=2, ensure_ascii=False)}")
    except:
        print(f"原始响应: {response.text}")
