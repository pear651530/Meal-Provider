import pytest
from fastapi.testclient import TestClient
from datetime import datetime
from ..models import User, DiningRecord

@pytest.fixture(autouse=True)
def cleanup_database(db):
    # Clean up all data before each test
    db.query(DiningRecord).delete()
    db.query(User).delete()
    db.commit()
    yield
    # Clean up after test
    db.query(DiningRecord).delete()
    db.query(User).delete()
    db.commit()

def test_get_unpaid_users_with_valid_api_key(client: TestClient, db):
    # Create test users
    user1 = User(username="user1", hashed_password="password", role="employee")
    user2 = User(username="user2", hashed_password="password", role="employee")
    db.add_all([user1, user2])
    db.commit()
    db.refresh(user1)
    db.refresh(user2)

    # Store user data before creating dining records
    user1_id = user1.id
    user1_username = user1.username
    user2_id = user2.id
    user2_username = user2.username

    # Create unpaid dining records
    dining_record1 = DiningRecord(
        user_id=user1_id,
        order_id=1,
        menu_item_id=1,
        menu_item_name="Test Item 1",
        total_amount=100.0,
        payment_status="unpaid"
    )
    dining_record2 = DiningRecord(
        user_id=user2_id,
        order_id=2,
        menu_item_id=2,
        menu_item_name="Test Item 2",
        total_amount=200.0,
        payment_status="unpaid"
    )
    db.add_all([dining_record1, dining_record2])
    db.commit()

    # Make request with valid API key
    response = client.get(
        "/users/unpaid",
        headers={"X-API-Key": "mealprovider_admin_key"}
    )

    # Verify response
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    
    # Verify first user
    assert data[0]["user_id"] == user1_id
    assert data[0]["user_name"] == user1_username
    assert data[0]["unpaidAmount"] == 100.0
    
    # Verify second user
    assert data[1]["user_id"] == user2_id
    assert data[1]["user_name"] == user2_username
    assert data[1]["unpaidAmount"] == 200.0

def test_get_unpaid_users_without_api_key(client: TestClient):
    response = client.get("/users/unpaid")
    assert response.status_code == 422
    assert "detail" in response.json()

def test_get_unpaid_users_with_invalid_api_key(client: TestClient):
    response = client.get(
        "/users/unpaid",
        headers={"X-API-Key": "invalid_key"}
    )
    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid API key"

def test_get_unpaid_users_empty_list(client: TestClient, db):
    # Create a user with no unpaid records
    user = User(
        username="user3",
        hashed_password="password",
        role="employee"
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    # Store user data
    user_id = user.id

    # Create a paid dining record
    dining_record = DiningRecord(
        user_id=user_id,
        order_id=4,
        menu_item_id=1,
        menu_item_name="Test Item 1",
        total_amount=100.0,
        payment_status="paid"
    )
    db.add(dining_record)
    db.commit()

    # Test API call
    response = client.get(
        "/users/unpaid",
        headers={"X-API-Key": "mealprovider_admin_key"}
    )

    assert response.status_code == 200
    data = response.json()
    assert len(data) == 0  # No unpaid records 