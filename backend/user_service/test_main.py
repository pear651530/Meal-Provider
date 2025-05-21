import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from main import app, get_db
from database import Base
from models import User, DiningRecord, Review

# Create test database
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

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

@pytest.fixture
def test_user_data():
    return {
        "username": "testuser",
        "email": "test@example.com",
        "full_name": "Test User",
        "password": "testpassword123"
    }

@pytest.fixture
def test_user(test_user_data):
    response = client.post("/users/", json=test_user_data)
    assert response.status_code == 200
    return response.json()

def test_create_user(test_user_data):
    response = client.post("/users/", json=test_user_data)
    assert response.status_code == 200
    data = response.json()
    assert data["username"] == test_user_data["username"]
    assert data["full_name"] == test_user_data["full_name"]
    assert "id" in data
    assert "role" in data
    assert data["role"] == "employee"

# def test_create_duplicate_user(test_user):
#     response = client.post("/users/", json=test_user)
#     assert response.status_code == 400
#     assert response.json()["detail"] == "Email already registered"

# def test_login(test_user_data):
#     response = client.post(
#         "/token",
#         data={"username": test_user_data["username"], "password": test_user_data["password"]}
#     )
#     assert response.status_code == 200
#     data = response.json()
#     assert "access_token" in data
#     assert data["token_type"] == "bearer"

# def test_login_wrong_password(test_user_data):
#     response = client.post(
#         "/token",
#         data={"username": test_user_data["username"], "password": "wrongpassword"}
#     )
#     assert response.status_code == 401
#     assert response.json()["detail"] == "Incorrect username or password"

# def test_get_current_user(test_user_data):
#     # First login to get token
#     login_response = client.post(
#         "/token",
#         data={"username": test_user_data["username"], "password": test_user_data["password"]}
#     )
#     token = login_response.json()["access_token"]
    
#     # Test getting current user
#     response = client.get(
#         "/users/me",
#         headers={"Authorization": f"Bearer {token}"}
#     )
#     assert response.status_code == 200
#     data = response.json()
#     assert data["username"] == test_user_data["username"]
#     assert data["email"] == test_user_data["email"]

# def test_get_user_dining_records(test_user_data):
#     # First login to get token
#     login_response = client.post(
#         "/token",
#         data={"username": test_user_data["username"], "password": test_user_data["password"]}
#     )
#     token = login_response.json()["access_token"]
    
#     # Test getting dining records
#     response = client.get(
#         "/users/1/dining-records/",
#         headers={"Authorization": f"Bearer {token}"}
#     )
#     assert response.status_code == 200
#     assert isinstance(response.json(), list)

# def test_create_review(test_user_data):
#     # First login to get token
#     login_response = client.post(
#         "/token",
#         data={"username": test_user_data["username"], "password": test_user_data["password"]}
#     )
#     token = login_response.json()["access_token"]
    
#     # Create a review
#     review_data = {
#         "rating": 5,
#         "comment": "Great service!",
#         "dining_record_id": 1
#     }
    
#     response = client.post(
#         "/dining-records/1/reviews/",
#         json=review_data,
#         headers={"Authorization": f"Bearer {token}"}
#     )
#     assert response.status_code == 404  # This will fail because we don't have a dining record with ID 1 