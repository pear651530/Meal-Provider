import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from ..main import app, get_db
from ..models import Base
from ..database import Base

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

def create_test_user(username: str, password: str, role: str = "employee"):
    response = client.post(
        "/users/",
        json={"username": username, "password": password}
    )
    if response.status_code == 200:
        # Update role if needed
        if role != "employee":
            # Get super admin token
            super_admin_token = get_super_admin_token()
            client.put(
                f"/users/{response.json()['id']}/role",
                params={"new_role": role},
                headers={"Authorization": f"Bearer {super_admin_token}"}
            )
    return response

def get_super_admin_token():
    response = client.post(
        "/token",
        data={"username": "superadmin", "password": "superadmin123"}
    )
    return response.json()["access_token"]

def get_user_token(username: str, password: str):
    response = client.post(
        "/token",
        data={"username": username, "password": password}
    )
    return response.json()["access_token"]

@pytest.fixture(autouse=True)
def setup_database():
    # Create tables
    Base.metadata.create_all(bind=engine)
    yield
    # Drop tables after test
    Base.metadata.drop_all(bind=engine)

def test_super_admin_creation():
    """Test that super admin is created on startup"""
    # The super admin should be created automatically on startup
    response = client.post(
        "/token",
        data={"username": "superadmin", "password": "superadmin123"}
    )
    assert response.status_code == 200
    assert "access_token" in response.json()

def test_role_update_by_super_admin():
    """Test that super admin can update user roles"""
    # Create a regular user
    create_test_user("testuser", "testpass")
    
    # Get super admin token
    super_admin_token = get_super_admin_token()
    
    # Get the user's ID (you might need to implement a way to get this)
    response = client.get(
        "/users/me",
        headers={"Authorization": f"Bearer {get_user_token('testuser', 'testpass')}"}
    )
    user_id = response.json()["id"]
    
    # Update user role to admin
    response = client.put(
        f"/users/{user_id}/role",
        params={"new_role": "admin"},
        headers={"Authorization": f"Bearer {super_admin_token}"}
    )
    assert response.status_code == 200
    assert response.json()["role"] == "admin"

def test_role_update_by_non_super_admin():
    """Test that non-super admin cannot update user roles"""
    # Create two regular users
    create_test_user("user1", "pass1")
    create_test_user("user2", "pass2")
    
    # Get user1's token
    user1_token = get_user_token("user1", "pass1")
    
    # Get user2's ID
    response = client.get(
        "/users/me",
        headers={"Authorization": f"Bearer {get_user_token('user2', 'pass2')}"}
    )
    user2_id = response.json()["id"]
    
    # Try to update user2's role
    response = client.put(
        f"/users/{user2_id}/role",
        params={"new_role": "admin"},
        headers={"Authorization": f"Bearer {user1_token}"}
    )
    assert response.status_code == 403

def test_invalid_role_update():
    """Test that invalid roles are rejected"""
    # Create a regular user
    create_test_user("testuser", "testpass")
    
    # Get super admin token
    super_admin_token = get_super_admin_token()
    
    # Get the user's ID
    response = client.get(
        "/users/me",
        headers={"Authorization": f"Bearer {get_user_token('testuser', 'testpass')}"}
    )
    user_id = response.json()["id"]
    
    # Try to update to invalid role
    response = client.put(
        f"/users/{user_id}/role",
        params={"new_role": "invalid_role"},
        headers={"Authorization": f"Bearer {super_admin_token}"}
    )
    assert response.status_code == 400

def test_cannot_modify_super_admin():
    """Test that super admin's role cannot be modified"""
    # Get super admin token
    super_admin_token = get_super_admin_token()
    
    # Get super admin's ID
    response = client.get(
        "/users/me",
        headers={"Authorization": f"Bearer {super_admin_token}"}
    )
    super_admin_id = response.json()["id"]
    
    # Try to modify super admin's role
    response = client.put(
        f"/users/{super_admin_id}/role",
        params={"new_role": "admin"},
        headers={"Authorization": f"Bearer {super_admin_token}"}
    )
    assert response.status_code == 403

def test_update_nonexistent_user():
    """Test updating role of non-existent user"""
    # Get super admin token
    super_admin_token = get_super_admin_token()
    
    # Try to update non-existent user
    response = client.put(
        "/users/99999/role",
        params={"new_role": "admin"},
        headers={"Authorization": f"Bearer {super_admin_token}"}
    )
    assert response.status_code == 404 