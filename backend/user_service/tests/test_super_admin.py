import pytest
from fastapi.testclient import TestClient
from ..main import app
from ..models import User
from .conftest import client, db, create_test_user
from passlib.context import CryptContext
import time

# Password encryption configuration
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def test_super_admin_creation(db):
    # Create a super admin user
    super_admin = create_test_user(username="superadmin", password="superpass", role="super_admin")
    assert super_admin.role == "super_admin"

def test_role_update_by_super_admin(client, db):
    # Create a super admin and a regular user
    super_admin = create_test_user(username="superadmin", password="superpass", role="super_admin")
    regular_user = create_test_user(username="regular", password="regularpass", role="employee")
    
    # Get token for super admin
    response = client.post(
        "/token",
        data={"username": "superadmin", "password": "superpass"}
    )
    assert response.status_code == 200
    token = response.json()["access_token"]
    
    # Update regular user's role
    response = client.put(
        f"/users/{regular_user.id}/role",
        headers={"Authorization": f"Bearer {token}"},
        params={"new_role": "admin"}
    )
    assert response.status_code == 200
    assert response.json()["role"] == "admin"

def test_role_update_by_non_super_admin(client, db):
    # Create an admin and a regular user directly in the test database
    timestamp = int(time.time())
    admin_password = "adminpass"
    admin = User(
        username=f"testadmin_{timestamp}",
        hashed_password=pwd_context.hash(admin_password),
        role="admin"
    )
    db.add(admin)
    db.commit()
    db.refresh(admin)
    
    regular_user = User(
        username=f"regular_{timestamp}",
        hashed_password=pwd_context.hash("regularpass"),
        role="employee"
    )
    db.add(regular_user)
    db.commit()
    db.refresh(regular_user)
    
    # Get token for admin
    response = client.post(
        "/token",
        data={"username": f"testadmin_{timestamp}", "password": admin_password}
    )
    assert response.status_code == 200
    token = response.json()["access_token"]
    
    # Try to update regular user's role
    response = client.put(
        f"/users/{regular_user.id}/role",
        headers={"Authorization": f"Bearer {token}"},
        params={"new_role": "admin"}
    )
    assert response.status_code == 403

def test_invalid_role_update(client, db):
    # Create a super admin and a regular user
    super_admin = create_test_user(username="superadmin", password="superpass", role="super_admin")
    regular_user = create_test_user(username="regular", password="regularpass", role="employee")
    
    # Get token for super admin
    response = client.post(
        "/token",
        data={"username": "superadmin", "password": "superpass"}
    )
    assert response.status_code == 200
    token = response.json()["access_token"]
    
    # Try to update with invalid role
    response = client.put(
        f"/users/{regular_user.id}/role",
        headers={"Authorization": f"Bearer {token}"},
        params={"new_role": "invalid_role"}
    )
    assert response.status_code == 400

def test_cannot_modify_super_admin(client, db):
    # Create two super admins
    super_admin1 = create_test_user(username="superadmin1", password="superpass", role="super_admin")
    super_admin2 = create_test_user(username="superadmin2", password="superpass", role="super_admin")
    
    # Get token for first super admin
    response = client.post(
        "/token",
        data={"username": "superadmin1", "password": "superpass"}
    )
    assert response.status_code == 200
    token = response.json()["access_token"]
    
    # Try to modify second super admin's role
    response = client.put(
        f"/users/{super_admin2.id}/role",
        headers={"Authorization": f"Bearer {token}"},
        params={"new_role": "admin"}
    )
    assert response.status_code == 403

def test_update_nonexistent_user(client, db):
    # Create a super admin
    super_admin = create_test_user(username="superadmin", password="superpass", role="super_admin")
    
    # Get token for super admin
    response = client.post(
        "/token",
        data={"username": "superadmin", "password": "superpass"}
    )
    assert response.status_code == 200
    token = response.json()["access_token"]
    
    # Try to update nonexistent user
    response = client.put(
        "/users/999/role",
        headers={"Authorization": f"Bearer {token}"},
        params={"new_role": "admin"}
    )
    assert response.status_code == 404 