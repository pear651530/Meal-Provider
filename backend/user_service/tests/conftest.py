import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from passlib.context import CryptContext
from datetime import datetime

from ..main import app
from ..models import Base, User, DiningRecord, Review
from ..database import get_db

# Create test database
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Password encryption configuration
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Create test database tables
Base.metadata.create_all(bind=engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)

# Test data
test_user = {
    "username": "testuser",
    "password": "testpass"
}

test_dining_record = {
    "date": datetime.now().date().isoformat(),
    "meal_type": "lunch",
    "restaurant_id": 1,
    "menu_item_id": 1,
    "menu_item_name": "Test Menu Item"
}

test_review = {
    "rating": "good",
    "comment": "Great meal!"
}

@pytest.fixture
def test_db():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)

@pytest.fixture
def auth_headers():
    # Create test user
    response = client.post("/users/", json=test_user)
    assert response.status_code == 200
    
    # Login to get token
    response = client.post("/token", data={
        "username": test_user["username"],
        "password": test_user["password"]
    })
    assert response.status_code == 200
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}

@pytest.fixture
def test_user_instance(test_db):
    db = TestingSessionLocal()
    user = User(
        username=test_user["username"],
        hashed_password=test_user["password"],  # In real app, this would be hashed
        role="employee"
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

@pytest.fixture
def test_dining_record_instance(test_user_instance, test_db):
    db = TestingSessionLocal()
    dining_record = DiningRecord(
        user_id=test_user_instance.id,
        date=datetime.now().date(),
        meal_type="lunch",
        restaurant_id=1,
        menu_item_id=1,
        menu_item_name="Test Menu Item"
    )
    db.add(dining_record)
    db.commit()
    db.refresh(dining_record)
    return dining_record

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
            pass  # Don't close the session here
    
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