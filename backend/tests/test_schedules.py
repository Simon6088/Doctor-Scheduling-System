import pytest
from datetime import date
from app.models import User, RoleEnum, ShiftType, ShiftTrade, Schedule, TradeStatus
from app.core.security import get_password_hash

def test_generate_schedule_permission(client):
    # Anonymous
    response = client.post("/schedules/generate?start_date=2026-01-01")
    assert response.status_code == 401

def test_create_trade_flow(client, db):
    # 1. Setup users
    pwd = get_password_hash("pass")
    docA = User(username="docA", hashed_password=pwd, role=RoleEnum.DOCTOR)
    docB = User(username="docB", hashed_password=pwd, role=RoleEnum.DOCTOR)
    db.add(docA)
    db.add(docB)
    db.commit()
    
    # 2. Setup Shift for DocA
    shift = Schedule(date=date(2026, 1, 1), doctor_id=docA.id, shift_type_id=1, status="confirmed") # assuming shift type 1 exists
    # We need shift type
    st = ShiftType(id=1, name="Day", start_time="08:00", end_time="17:00")
    db.add(st)
    db.add(shift)
    db.commit()
    
    # 3. Login as DocA
    login_resp = client.post("/token", data={"username": "docA", "password": "pass"})
    tokenA = login_resp.json()["access_token"]
    headersA = {"Authorization": f"Bearer {tokenA}"}
    
    # 4. Create Trade
    trade_payload = {
        "request_shift_id": shift.id,
        "target_doctor_id": docB.id,
        "reason": "Test trade"
    }
    resp = client.post("/trades/", json=trade_payload, headers=headersA)
    assert resp.status_code == 200
    trade_data = resp.json()
    assert trade_data["status"] == "pending"
    assert trade_data["requester_id"] == docA.id
    
    # 5. Login as DocB
    login_respB = client.post("/token", data={"username": "docB", "password": "pass"})
    tokenB = login_respB.json()["access_token"]
    headersB = {"Authorization": f"Bearer {tokenB}"}
    
    # 6. Accept Trade
    trade_id = trade_data["id"]
    resp = client.put(f"/trades/{trade_id}/respond?action=accept", headers=headersB)
    assert resp.status_code == 200
    assert resp.json()["status"] == "accepted"
