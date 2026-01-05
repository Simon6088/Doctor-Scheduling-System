from app.models import User, RoleEnum
from app.core.security import get_password_hash

def test_create_user(client):
    response = client.post(
        "/users/",
        json={"username": "testuser", "password": "password", "full_name": "Test User", "role": "doctor"}
    )
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["username"] == "testuser"
    assert "id" in data

def test_login(client, db):
    # Create user first
    password = "password"
    hashed = get_password_hash(password)
    user = User(username="loginuser", hashed_password=hashed, role=RoleEnum.DOCTOR)
    db.add(user)
    db.commit()
    
    response = client.post(
        "/token",
        data={"username": "loginuser", "password": password}
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"

def test_login_wrong_password(client, db):
    # Create user
    password = "password"
    hashed = get_password_hash(password)
    user = User(username="badpassuser", hashed_password=hashed, role=RoleEnum.DOCTOR)
    db.add(user)
    db.commit()
    
    response = client.post(
        "/token",
        data={"username": "badpassuser", "password": "wrongpassword"}
    )
    assert response.status_code == 401
