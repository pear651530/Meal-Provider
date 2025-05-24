import pytest
from datetime import datetime
from models import User, DiningRecord
from sqlalchemy.orm import Session

# Test data
VALID_API_KEY = "mealprovider_admin_key"
INVALID_API_KEY = "wrong_key"

@pytest.fixture(autouse=True)
def cleanup_database(db: Session):
    # Clean up all data before each test
    db.query(DiningRecord).delete()
    db.query(User).delete()
    db.commit()
    yield
    # Clean up after test
    db.query(DiningRecord).delete()
    db.query(User).delete()
    db.commit()

def test_get_unpaid_users_with_valid_api_key(client, db: Session):
    # Create test users
    user1 = User(
        username="user1",
        full_name="Alice",
        hashed_password="password",
        role="employee"
    )
    user2 = User(
        username="user2",
        full_name="Bob",
        hashed_password="password",
        role="employee"
    )
    db.add_all([user1, user2])
    db.commit()

    # Create unpaid dining records
    dining_record1 = DiningRecord(
        user_id=user1.id,
        order_id=1,
        total_amount=120.0,
        payment_status="unpaid"
    )
    dining_record2 = DiningRecord(
        user_id=user1.id,
        order_id=2,
        total_amount=120.0,
        payment_status="unpaid"
    )
    dining_record3 = DiningRecord(
        user_id=user2.id,
        order_id=3,
        total_amount=360.0,
        payment_status="unpaid"
    )
    db.add_all([dining_record1, dining_record2, dining_record3])
    db.commit()

    # Test API call
    response = client.get(
        "/users/unpaid",
        headers={"X-API-Key": VALID_API_KEY}
    )

    assert response.status_code == 200
    data = response.json()
    
    # Verify response format and data
    assert len(data) == 2  # Two users with unpaid records
    
    # Find Alice's record
    alice_record = next(item for item in data if item["user_name"] == "Alice")
    assert alice_record["user_id"] == user1.id
    assert alice_record["unpaidAmount"] == 240.0  # 120 + 120
    
    # Find Bob's record
    bob_record = next(item for item in data if item["user_name"] == "Bob")
    assert bob_record["user_id"] == user2.id
    assert bob_record["unpaidAmount"] == 360.0

def test_get_unpaid_users_with_invalid_api_key(client):
    response = client.get(
        "/users/unpaid",
        headers={"X-API-Key": INVALID_API_KEY}
    )
    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid API key"

def test_get_unpaid_users_without_api_key(client):
    response = client.get("/users/unpaid")
    assert response.status_code == 422  # Validation error for missing header

def test_get_unpaid_users_empty_list(client, db: Session):
    # Create a user with no unpaid records
    user = User(
        username="user3",
        full_name="Charlie",
        hashed_password="password",
        role="employee"
    )
    db.add(user)
    db.commit()

    # Create a paid dining record
    dining_record = DiningRecord(
        user_id=user.id,
        order_id=4,
        total_amount=100.0,
        payment_status="paid"
    )
    db.add(dining_record)
    db.commit()

    # Test API call
    response = client.get(
        "/users/unpaid",
        headers={"X-API-Key": VALID_API_KEY}
    )

    assert response.status_code == 200
    data = response.json()
    assert len(data) == 0  # No unpaid records 