import pytest
from datetime import datetime
from models import DiningRecord
from fastapi import status

def test_get_dining_record(client, test_user_token, test_user, db):
    # Clean up any existing dining records
    db.query(DiningRecord).delete()
    db.commit()

    # Create a test dining record
    dining_record = DiningRecord(
        user_id=test_user.id,
        order_id=1,
        total_amount=100.0,
        payment_status="paid"
    )
    db.add(dining_record)
    db.commit()
    db.refresh(dining_record)

    # Test getting the dining record
    response = client.get(
        f"/dining-records/{dining_record.id}",
        headers={"Authorization": f"Bearer {test_user_token}"}
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["id"] == dining_record.id
    assert data["payment_status"] == "paid"
    
    # Test getting non-existent dining record
    response = client.get(
        "/dining-records/999",
        headers={"Authorization": f"Bearer {test_user_token}"}
    )
    assert response.status_code == status.HTTP_404_NOT_FOUND

def test_get_user_dining_records(client, test_user_token, test_user, db):
    # Clean up any existing dining records
    db.query(DiningRecord).delete()
    db.commit()

    # Create a test dining record
    dining_record = DiningRecord(
        user_id=test_user.id,
        order_id=1,
        total_amount=100.0,
        payment_status="paid"
    )
    db.add(dining_record)
    db.commit()
    db.refresh(dining_record)

    # Test getting all dining records for the user
    response = client.get(
        f"/users/{test_user.id}/dining-records/",
        headers={"Authorization": f"Bearer {test_user_token}"}
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert len(data) == 1
    assert data[0]["id"] == dining_record.id
    assert data[0]["payment_status"] == "paid"

def test_unauthorized_dining_record_access(client):
    # Test accessing dining record endpoints without authentication
    response = client.get("/dining-records/1")
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    response = client.get("/users/1/dining-records/")
    assert response.status_code == status.HTTP_401_UNAUTHORIZED 