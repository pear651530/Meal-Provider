import pytest
from fastapi import status
from fastapi.testclient import TestClient
from ..models import DiningRecord, User

def test_get_current_user(client: TestClient, test_user_token, test_user):
    response = client.get(
        "/users/me",
        headers={"Authorization": f"Bearer {test_user_token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["username"] == test_user.username
    assert data["role"] == test_user.role

def test_get_current_user_unauthorized(client: TestClient):
    response = client.get("/users/me")
    assert response.status_code == 401
    assert response.json()["detail"] == "Not authenticated"

def test_get_user_dining_records(client: TestClient, test_user_token, test_user, db):
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

    response = client.get(
        f"/users/{test_user.id}/dining-records",
        headers={"Authorization": f"Bearer {test_user_token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) == 1
    assert data[0]["order_id"] == 1
    assert data[0]["total_amount"] == 100.0
    assert data[0]["payment_status"] == "paid"
    assert data[0]["menu_item_id"] == 1
    assert data[0]["menu_item_name"] == "Test Menu Item"

def test_get_other_user_dining_records_unauthorized(client: TestClient, test_user_token, test_admin):
    response = client.get(
        f"/users/{test_admin.id}/dining-records",
        headers={"Authorization": f"Bearer {test_user_token}"}
    )
    assert response.status_code == 403
    assert response.json()["detail"] == "Not authorized"

def test_get_other_user_dining_records_admin(client: TestClient, test_admin_token, test_user):
    response = client.get(
        f"/users/{test_user.id}/dining-records",
        headers={"Authorization": f"Bearer {test_admin_token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)

def test_get_all_users_admin(client: TestClient, test_admin_token, test_user, test_admin, db):
    response = client.get(
        "/users/all",
        headers={"Authorization": f"Bearer {test_admin_token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    # Should contain both test_user and test_admin
    assert len(data) >= 2
    # Verify both users are in the response
    usernames = [user["username"] for user in data]
    assert test_user.username in usernames
    assert test_admin.username in usernames

def test_get_all_users_regular_user_unauthorized(client: TestClient, test_user_token):
    response = client.get(
        "/users/all",
        headers={"Authorization": f"Bearer {test_user_token}"}
    )
    assert response.status_code == 403
    assert response.json()["detail"] == "Not authorized. Admin or Super Admin access required."

def test_get_all_users_unauthorized(client: TestClient):
    response = client.get("/users/all")
    assert response.status_code == 401
    assert response.json()["detail"] == "Not authenticated" 