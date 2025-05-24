import pytest
from fastapi import status
from ..models import Review, DiningRecord
from sqlalchemy.orm import Session

def test_create_review(client, test_user_token, test_user, db):
    # Create a test dining record
    from ..models import DiningRecord
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
    db.refresh(dining_record)  # Refresh to ensure we have the ID

    # Store the ID before making the request
    dining_record_id = dining_record.id

    response = client.post(
        f"/dining-records/{dining_record_id}/reviews/",
        json={
            "rating": "good",
            "comment": "Great service!"
        },
        headers={"Authorization": f"Bearer {test_user_token}"}
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["rating"] == "good"
    assert data["comment"] == "Great service!"
    assert data["user_id"] == test_user.id
    assert data["dining_record_id"] == dining_record_id

def test_create_review_nonexistent_dining_record(client, test_user_token):
    response = client.post(
        "/dining-records/999/reviews/",
        json={
            "rating": "good",
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
            "rating": "good",
            "comment": "Great service!"
        }
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED

@pytest.fixture
def test_review_instance(db: Session, test_dining_record_instance):
    review = Review(
        user_id=test_dining_record_instance.user_id,
        dining_record_id=test_dining_record_instance.id,
        rating="good",
        comment="Great meal!"
    )
    db.add(review)
    db.commit()
    db.refresh(review)
    return review

def test_get_dining_record_review(client, test_user_token, test_user, db):
    # Create a test dining record and review
    from ..models import DiningRecord
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

    review = Review(
        user_id=test_user.id,
        dining_record_id=dining_record.id,
        rating="good",
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
    assert data["rating"] == "good"
    assert data["comment"] == "Great meal!"
    
    # Test getting review for non-existent dining record
    response = client.get(
        "/dining-records/999/reviews/",
        headers={"Authorization": f"Bearer {test_user_token}"}
    )
    assert response.status_code == status.HTTP_404_NOT_FOUND

def test_update_review(client, test_user_token, test_user, db):
    # Create a test dining record and review
    from ..models import DiningRecord
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

    review = Review(
        user_id=test_user.id,
        dining_record_id=dining_record.id,
        rating="good",
        comment="Great meal!"
    )
    db.add(review)
    db.commit()

    # Test updating the review
    updated_review = {
        "rating": "bad",
        "comment": "Excellent meal!"
    }
    response = client.put(
        f"/dining-records/{dining_record.id}/reviews/",
        json=updated_review,
        headers={"Authorization": f"Bearer {test_user_token}"}
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["rating"] == "bad"
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
        json={"rating": "good", "comment": "test"}
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    response = client.put(
        "/dining-records/1/reviews/",
        json={"rating": "good", "comment": "test"}
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED

def test_get_menu_item_rating(client, test_user_token, test_user, db):
    # Clean up any existing reviews and dining records for this menu item
    menu_item_id = 1
    menu_item_name = "Test Menu Item"
    
    # Delete existing reviews and dining records
    db.query(Review).delete()
    db.query(DiningRecord).delete()
    db.commit()
    
    # Create first dining record and review (good)
    dining_record1 = DiningRecord(
        user_id=test_user.id,
        order_id=1,
        menu_item_id=menu_item_id,
        menu_item_name=menu_item_name,
        total_amount=100.0,
        payment_status="paid"
    )
    db.add(dining_record1)
    db.commit()
    db.refresh(dining_record1)
    
    review1 = Review(
        user_id=test_user.id,
        dining_record_id=dining_record1.id,
        rating="good",
        comment="Great meal!"
    )
    db.add(review1)
    
    # Create second dining record and review (good)
    dining_record2 = DiningRecord(
        user_id=test_user.id,
        order_id=2,
        menu_item_id=menu_item_id,
        menu_item_name=menu_item_name,
        total_amount=150.0,
        payment_status="paid"
    )
    db.add(dining_record2)
    db.commit()
    db.refresh(dining_record2)
    
    review2 = Review(
        user_id=test_user.id,
        dining_record_id=dining_record2.id,
        rating="good",
        comment="Another great meal!"
    )
    db.add(review2)
    
    # Create third dining record and review (bad)
    dining_record3 = DiningRecord(
        user_id=test_user.id,
        order_id=3,
        menu_item_id=menu_item_id,
        menu_item_name=menu_item_name,
        total_amount=200.0,
        payment_status="paid"
    )
    db.add(dining_record3)
    db.commit()
    db.refresh(dining_record3)
    
    review3 = Review(
        user_id=test_user.id,
        dining_record_id=dining_record3.id,
        rating="bad",
        comment="Not so good"
    )
    db.add(review3)
    db.commit()
    
    # Test getting the rating statistics
    response = client.get(f"/ratings/{menu_item_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["menu_item_id"] == menu_item_id
    assert data["menu_item_name"] == menu_item_name
    assert data["total_reviews"] == 3  # Three reviews
    assert data["good_reviews"] == 2  # Two good reviews
    assert data["good_ratio"] == 2/3  # Two out of three reviews are good
    
    # Test getting rating for non-existent menu item
    response = client.get("/ratings/999")
    assert response.status_code == 404
    assert response.json()["detail"] == "Menu item not found"

def test_get_menu_item_rating_no_reviews(client, test_user_token, test_user, db):
    # Create a dining record without any reviews
    menu_item_id = 2
    menu_item_name = "Another Menu Item"
    
    dining_record = DiningRecord(
        user_id=test_user.id,
        order_id=3,
        menu_item_id=menu_item_id,
        menu_item_name=menu_item_name,
        total_amount=200.0,
        payment_status="paid"
    )
    db.add(dining_record)
    db.commit()
    
    # Test getting the rating statistics
    response = client.get(f"/ratings/{menu_item_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["menu_item_id"] == menu_item_id
    assert data["menu_item_name"] == menu_item_name
    assert data["total_reviews"] == 0  # No reviews
    assert data["good_reviews"] == 0
    assert data["good_ratio"] == 0 