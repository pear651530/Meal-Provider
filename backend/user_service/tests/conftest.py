import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from passlib.context import CryptContext

from main import app
from models import Base, User, DiningRecord, Review
from database import get_db

# Create test database
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Password encryption configuration
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

@pytest.fixture(scope="session", autouse=True)
def create_tables():
    Base.metadata.drop_all(bind=engine)  # Clean up any existing tables
    Base.metadata.create_all(bind=engine)  # Create fresh tables
    yield
    Base.metadata.drop_all(bind=engine)

@pytest.fixture(scope="function")
def db():
    # Create a new session for each test
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.rollback()  # Rollback any pending changes
        db.close()

@pytest.fixture(scope="function")
def client(db):
    def override_get_db():
        try:
            yield db
        finally:
            db.close()
    
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()

@pytest.fixture(scope="function")
def test_user(db):
    # First check if user exists
    existing_user = db.query(User).filter(User.username == "testuser").first()
    if existing_user:
        return existing_user
        
    # If not, create new user
    hashed_password = pwd_context.hash("password123")
    user = User(
        username="testuser",
        full_name="Test User",
        hashed_password=hashed_password,
        role="employee"
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

@pytest.fixture(scope="function")
def test_user_token(client, test_user):
    response = client.post(
        "/token",
        data={"username": "testuser", "password": "password123"}
    )
    return response.json()["access_token"] 