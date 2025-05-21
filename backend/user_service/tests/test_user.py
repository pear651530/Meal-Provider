import pytest
from fastapi import status

def test_get_current_user(client, test_user_token):
    response = client.get(
        "/users/me",
        headers={"Authorization": f"Bearer {test_user_token}"}
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["username"] == "testuser"
    assert data["full_name"] == "Test User"
    assert data["role"] == "employee"

def test_get_current_user_unauthorized(client):
    response = client.get("/users/me")
    assert response.status_code == status.HTTP_401_UNAUTHORIZED

def test_get_user_dining_records(client, test_user_token, test_user, db):
    # Create a test dining record
    from models import DiningRecord
    dining_record = DiningRecord(
        user_id=test_user.id,
        order_id=1,
        total_amount=100.0,
        payment_status="paid"
    )
    db.add(dining_record)
    db.commit()

    response = client.get(
        f"/users/{test_user.id}/dining-records/",
        headers={"Authorization": f"Bearer {test_user_token}"}
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert isinstance(data, list)
    assert len(data) == 1
    assert data[0]["order_id"] == 1
    assert data[0]["total_amount"] == 100.0
    assert data[0]["payment_status"] == "paid"

def test_get_other_user_dining_records_unauthorized(client, test_user_token):
    response = client.get(
        "/users/999/dining-records/",
        headers={"Authorization": f"Bearer {test_user_token}"}
    )
    assert response.status_code == status.HTTP_403_FORBIDDEN 