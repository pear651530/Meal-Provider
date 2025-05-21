import pytest
from fastapi import status

def test_create_review(client, test_user_token, test_user, db):
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
    db.refresh(dining_record)  # Refresh to ensure we have the ID

    # Store the ID before making the request
    dining_record_id = dining_record.id

    response = client.post(
        f"/dining-records/{dining_record_id}/reviews/",
        json={
            "rating": 5,
            "comment": "Great service!"
        },
        headers={"Authorization": f"Bearer {test_user_token}"}
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["rating"] == 5
    assert data["comment"] == "Great service!"
    assert data["user_id"] == test_user.id
    assert data["dining_record_id"] == dining_record_id

def test_create_review_nonexistent_dining_record(client, test_user_token):
    response = client.post(
        "/dining-records/999/reviews/",
        json={
            "rating": 5,
            "comment": "Great service!"
        },
        headers={"Authorization": f"Bearer {test_user_token}"}
    )
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json()["detail"] == "Dining record not found"

def test_create_review_unauthorized(client):
    response = client.post(
        "/dining-records/1/reviews/",
        json={
            "rating": 5,
            "comment": "Great service!"
        }
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED 