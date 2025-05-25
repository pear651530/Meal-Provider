import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from datetime import datetime
from passlib.context import CryptContext

from ..main import app
from .. import models, schemas, database
from .conftest import create_test_user, create_test_notification

# Password encryption configuration
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

@pytest.fixture(autouse=True)
def cleanup_database(db):
    """Clean up notifications before each test"""
    db.query(models.Notification).delete()
    db.commit()
    yield
    db.query(models.Notification).delete()
    db.commit()

client = TestClient(app)

def test_get_user_notifications_success(client, test_user, test_user_token, db):
    """Test successful retrieval of user notifications"""
    # Create test notifications
    notifications = [
        create_test_notification(test_user.id, "Test notification 1", notification_type="system"),
        create_test_notification(test_user.id, "Test notification 2", notification_type="billing")
    ]
    
    # Get notifications
    response = client.get(
        f"/users/{test_user.id}/notifications",
        headers={"Authorization": f"Bearer {test_user_token}"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    # Check that we have the required fields in the response
    for notification in data:
        assert "id" in notification
        assert "user_id" in notification
        assert "message" in notification
        assert "notification_type" in notification
        assert "is_read" in notification
        assert "created_at" in notification
        assert notification["notification_type"] in ["system", "billing"]

def test_get_user_notifications_unauthorized(client, test_user, test_user_token, db):
    """Test unauthorized access to notifications"""
    # Create another test user
    user2 = create_test_user(username="user2", password="testpassword")
    
    # Create notification for user2
    create_test_notification(user2.id, "Test notification", notification_type="system")
    
    # Try to access user2's notifications with user1's token
    response = client.get(
        f"/users/{user2.id}/notifications",
        headers={"Authorization": f"Bearer {test_user_token}"}
    )
    
    assert response.status_code == 403

def test_mark_notification_read_success(client, test_user, test_user_token, db):
    """Test successful marking of notification as read"""
    # Create test notification
    notification = create_test_notification(test_user.id, "Test notification", notification_type="system")
    
    # Mark notification as read
    response = client.put(
        f"/notifications/{notification.id}/read",
        headers={"Authorization": f"Bearer {test_user_token}"}
    )
    
    assert response.status_code == 200
    data = response.json()
    # Check that we have the required fields in the response
    assert "id" in data
    assert "user_id" in data
    assert "message" in data
    assert "notification_type" in data
    assert "is_read" in data
    assert "created_at" in data
    assert data["is_read"] == True
    assert data["id"] == notification.id
    assert data["notification_type"] == "system"

def test_mark_notification_read_not_found(client, test_user, test_user_token, db):
    """Test marking non-existent notification as read"""
    # Try to mark non-existent notification as read
    response = client.put(
        "/notifications/999/read",
        headers={"Authorization": f"Bearer {test_user_token}"}
    )
    
    assert response.status_code == 404

def test_mark_notification_read_unauthorized(client, test_user, test_user_token, db):
    """Test unauthorized marking of notification as read"""
    # Create another test user and notification
    user2 = create_test_user(username="user2", password="testpassword")
    notification = create_test_notification(user2.id, "Test notification", notification_type="system")
    
    # Try to mark user2's notification as read with user1's token
    response = client.put(
        f"/notifications/{notification.id}/read",
        headers={"Authorization": f"Bearer {test_user_token}"}
    )
    
    assert response.status_code == 404  # Returns 404 because notification not found for user1 