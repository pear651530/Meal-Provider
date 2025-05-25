import pytest
from datetime import datetime
from ..models import DiningRecord
from fastapi import status
from fastapi.testclient import TestClient

def test_get_dining_record(client, test_user_token, test_user, db):
    # Clean up any existing dining records
    db.query(DiningRecord).delete()
    db.commit()

    # Create a test dining record
    dining_record = DiningRecord(
        user_id=test_user.id,
        order_id=1,
        menu_item_id=1,
        menu_item_name="Test Menu Item",
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
    assert data["menu_item_id"] == 1
    assert data["menu_item_name"] == "Test Menu Item"
    
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
        menu_item_id=1,
        menu_item_name="Test Menu Item",
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
    assert data[0]["menu_item_id"] == 1
    assert data[0]["menu_item_name"] == "Test Menu Item"

def test_unauthorized_dining_record_access(client):
    # Test accessing dining record endpoints without authentication
    response = client.get("/dining-records/1")
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    response = client.get("/users/1/dining-records/")
    assert response.status_code == status.HTTP_401_UNAUTHORIZED

def test_get_all_dining_records(client: TestClient, db):
    # Clean up any existing dining records
    db.query(DiningRecord).delete()
    db.commit()

    # Create multiple test dining records
    dining_records = [
        DiningRecord(
            user_id=1,
            order_id=1,
            menu_item_id=1,
            menu_item_name="Test Menu Item 1",
            total_amount=100.0,
            payment_status="paid"
        ),
        DiningRecord(
            user_id=1,
            order_id=2,
            menu_item_id=2,
            menu_item_name="Test Menu Item 2",
            total_amount=200.0,
            payment_status="unpaid"
        )
    ]
    for record in dining_records:
        db.add(record)
    db.commit()

    # Test getting all dining records with API key
    response = client.get(
        "/dining-records/",
        headers={"X-API-Key": "mealprovider_admin_key"}
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    
    # Verify the first record
    assert data[0]["menu_item_name"] == "Test Menu Item 1"
    assert data[0]["payment_status"] == "paid"
    assert data[0]["total_amount"] == 100.0
    
    # Verify the second record
    assert data[1]["menu_item_name"] == "Test Menu Item 2"
    assert data[1]["payment_status"] == "unpaid"
    assert data[1]["total_amount"] == 200.0

    # Test accessing without API key
    response = client.get("/dining-records/")
    assert response.status_code == 422  # FastAPI returns 422 for missing required header
    assert "detail" in response.json()

    # Test accessing with invalid API key
    response = client.get(
        "/dining-records/",
        headers={"X-API-Key": "invalid_key"}
    )
    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid API key" 