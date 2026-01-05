import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.main import app
from app.database import Base, get_db
from app.models import User, RoleEnum
from app.core.security import get_password_hash

# Use an in-memory SQLite database for tests, or a separate test PG DB.
# For simplicity in this environment, let's use SQLite or just mock?
# Since code uses Postgres specific things (maybe?), SQLite might fail if we used Array types etc.
# But our models are simple. Let's try SQLite for speed.
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(scope="module")
def db_engine():
    Base.metadata.create_all(bind=engine)
    yield engine
    Base.metadata.drop_all(bind=engine)

@pytest.fixture(scope="function")
def db(db_engine):
    connection = db_engine.connect()
    transaction = connection.begin()
    session = TestingSessionLocal(bind=connection)
    yield session
    session.close()
    transaction.rollback()
    connection.close()

@pytest.fixture(scope="function")
def client(db):
    def override_get_db():
        try:
            yield db
        finally:
            pass
    
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c

@pytest.fixture
def admin_token_headers(client):
    # Create admin
    hashed = get_password_hash("admin123")
    # We need to manually insert because API might be protected
    # But wait, we are using the same DB session?
    # Actually, we can just use the registration endpoint if it's open (it is for now)
    # Or insert directly to DB fixture
    # Let's insert directly.
    # Note: SQLite multithreading might be an issue with TestClient? TestClient is sync.
    pass 
    # For now, let's just return a helper to create token
    return {}
