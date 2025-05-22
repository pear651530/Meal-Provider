import pytest
from fastapi import status
from models import Review
from sqlalchemy.orm import Session

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

@pytest.fixture
def test_review_instance(db: Session, test_dining_record_instance):
    review = Review(
        user_id=test_dining_record_instance.user_id,
        dining_record_id=test_dining_record_instance.id,
        rating=4,
        comment="Great meal!"
    )
    db.add(review)
    db.commit()
    db.refresh(review)
    return review

def test_get_dining_record_review(client, test_user_token, test_user, db):
    # Create a test dining record and review
    from models import DiningRecord
    dining_record = DiningRecord(
        user_id=test_user.id,
        order_id=1,
        total_amount=100.0,
        payment_status="paid"
    )
    db.add(dining_record)
    db.commit()
    db.refresh(dining_record)

    review = Review(
        user_id=test_user.id,
        dining_record_id=dining_record.id,
        rating=4,
        comment="Great meal!"
    )
    db.add(review)
    db.commit()

    # Test getting the review
    response = client.get(
        f"/dining-records/{dining_record.id}/reviews/",
        headers={"Authorization": f"Bearer {test_user_token}"}
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["rating"] == 4
    assert data["comment"] == "Great meal!"
    
    # Test getting review for non-existent dining record
    response = client.get(
        "/dining-records/999/reviews/",
        headers={"Authorization": f"Bearer {test_user_token}"}
    )
    assert response.status_code == status.HTTP_404_NOT_FOUND

def test_update_review(client, test_user_token, test_user, db):
    # Create a test dining record and review
    from models import DiningRecord
    dining_record = DiningRecord(
        user_id=test_user.id,
        order_id=1,
        total_amount=100.0,
        payment_status="paid"
    )
    db.add(dining_record)
    db.commit()
    db.refresh(dining_record)

    review = Review(
        user_id=test_user.id,
        dining_record_id=dining_record.id,
        rating=4,
        comment="Great meal!"
    )
    db.add(review)
    db.commit()

    # Test updating the review
    updated_review = {
        "rating": 5,
        "comment": "Excellent meal!"
    }
    response = client.put(
        f"/dining-records/{dining_record.id}/reviews/",
        json=updated_review,
        headers={"Authorization": f"Bearer {test_user_token}"}
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["rating"] == 5
    assert data["comment"] == "Excellent meal!"
    
    # Test updating non-existent review
    response = client.put(
        "/dining-records/999/reviews/",
        json=updated_review,
        headers={"Authorization": f"Bearer {test_user_token}"}
    )
    assert response.status_code == status.HTTP_404_NOT_FOUND

def test_unauthorized_review_access(client):
    # Test accessing review endpoints without authentication
    response = client.get("/dining-records/1/reviews/")
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    response = client.post(
        "/dining-records/1/reviews/",
        json={"rating": 5, "comment": "test"}
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    response = client.put(
        "/dining-records/1/reviews/",
        json={"rating": 5, "comment": "test"}
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED 