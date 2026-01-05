import requests

BASE_URL = "http://127.0.0.1:8000"

# 登录
login_resp = requests.post(f"{BASE_URL}/token", data={
    "username": "admin",
    "password": "admin123"
})

if login_resp.status_code != 200:
    print(f"登录失败: {login_resp.text}")
    exit(1)

token = login_resp.json()["access_token"]
headers = {"Authorization": f"Bearer {token}"}

# 测试获取排班
print("测试获取排班...")
resp = requests.get(f"{BASE_URL}/schedules/", headers=headers)
print(f"状态码: {resp.status_code}")
print(f"响应: {resp.text}")

if resp.status_code == 200:
    schedules = resp.json()
    print(f"\n成功获取 {len(schedules)} 条排班记录")
    if schedules:
        print("\n前 3 条记录:")
        for s in schedules[:3]:
            print(f"  - ID: {s['id']}, 日期: {s['date']}, 医生ID: {s['doctor_id']}, 班次: {s['shift_type_id']}")
else:
    print(f"\n获取失败！错误信息: {resp.text}")
