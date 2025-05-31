import pytest
from fastapi import status
from fastapi.testclient import TestClient
from ..models import Review, DiningRecord
from sqlalchemy.orm import Session
from datetime import datetime

def test_create_review(client: TestClient, test_user_token, test_dining_record_instance, db):
    # Clean up any existing reviews
    db.query(Review).delete()
    db.commit()

    # Create review data
    review_data = {
        "rating": "good",
        "comment": "Great meal!"
    }

    # Make request to create review
    response = client.post(
        f"/dining-records/{test_dining_record_instance.id}/reviews",
        json=review_data,
        headers={"Authorization": f"Bearer {test_user_token}"}
    )

    # Verify response
    assert response.status_code == 200
    data = response.json()
    assert data["rating"] == review_data["rating"]
    assert data["comment"] == review_data["comment"]
    assert data["user_id"] == test_dining_record_instance.user_id
    assert data["dining_record_id"] == test_dining_record_instance.id

    # Verify review was created in database
    db_review = db.query(Review).filter(
        Review.dining_record_id == test_dining_record_instance.id
    ).first()
    assert db_review is not None
    assert db_review.rating == review_data["rating"]
    assert db_review.comment == review_data["comment"]

def test_create_review_nonexistent_dining_record(client: TestClient, test_user_token):
    # Create review data
    review_data = {
        "rating": "good",
        "comment": "Great meal!"
    }

    # Make request with non-existent dining record ID
    response = client.post(
        "/dining-records/999/reviews",
        json=review_data,
        headers={"Authorization": f"Bearer {test_user_token}"}
    )

    # Verify response
    assert response.status_code == 404
    assert response.json()["detail"] == "Dining record not found"

def test_create_review_unauthorized(client: TestClient, test_dining_record_instance):
    # Create review data
    review_data = {
        "rating": "good",
        "comment": "Great meal!"
    }

    # Make request without token
    response = client.post(
        f"/dining-records/{test_dining_record_instance.id}/reviews",
        json=review_data
    )

    # Verify response
    assert response.status_code == 401
    assert response.json()["detail"] == "Not authenticated"

def test_create_review_wrong_user(client: TestClient, test_dining_record_instance, test_admin_token):
    # Create review data
    review_data = {
        "rating": "good",
        "comment": "Great meal!"
    }

    # Make request with different user's token
    response = client.post(
        f"/dining-records/{test_dining_record_instance.id}/reviews",
        json=review_data,
        headers={"Authorization": f"Bearer {test_admin_token}"}
    )

    # Verify response
    assert response.status_code == 403
    assert response.json()["detail"] == "Not authorized to review this dining record"

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

def test_get_dining_record_review(client: TestClient, test_user_token, test_user, db):
    # Create a test dining record and review
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
        f"/dining-records/{dining_record.id}/reviews",
        headers={"Authorization": f"Bearer {test_user_token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["rating"] == "good"
    assert data["comment"] == "Great meal!"
    
    # Test getting review for non-existent dining record
    response = client.get(
        "/dining-records/999/reviews",
        headers={"Authorization": f"Bearer {test_user_token}"}
    )
    assert response.status_code == 404
    assert response.json()["detail"] == "Dining record not found"

def test_update_review(client: TestClient, test_user_token, test_user, db):
    # Create a test dining record and review
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
        "comment": "Not so good"
    }
    response = client.put(
        f"/dining-records/{dining_record.id}/reviews",
        json=updated_review,
        headers={"Authorization": f"Bearer {test_user_token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["rating"] == "bad"
    assert data["comment"] == "Not so good"
    
    # Test updating non-existent review
    response = client.put(
        "/dining-records/999/reviews",
        json=updated_review,
        headers={"Authorization": f"Bearer {test_user_token}"}
    )
    assert response.status_code == 404
    assert response.json()["detail"] == "Dining record not found"

def test_unauthorized_review_access(client: TestClient):
    # Test accessing review endpoints without authentication
    response = client.get("/dining-records/1/reviews")
    assert response.status_code == 401
    assert response.json()["detail"] == "Not authenticated"
    
    response = client.post(
        "/dining-records/1/reviews",
        json={"rating": "good", "comment": "test"}
    )
    assert response.status_code == 401
    assert response.json()["detail"] == "Not authenticated"
    
    response = client.put(
        "/dining-records/1/reviews",
        json={"rating": "good", "comment": "test"}
    )
    assert response.status_code == 401
    assert response.json()["detail"] == "Not authenticated"

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

def test_get_menu_item_reviews(client, test_user_token, test_user, db):
    # Clean up any existing reviews and dining records
    db.query(Review).delete()
    db.query(DiningRecord).delete()
    db.commit()
    
    # Create test data
    menu_item_id = 1
    menu_item_name = "Test Menu Item"
    
    # Create first dining record and review
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
    
    # Create second dining record and review
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
        rating="bad",
        comment="Not so good"
    )
    db.add(review2)
    db.commit()
    
    # Test getting reviews for the menu item
    response = client.get(
        f"/reviews/{menu_item_id}",
        headers={"Authorization": f"Bearer {test_user_token}"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    
    # Verify the reviews are returned in descending order by created_at
    assert data[0]["rating"] == "bad"
    assert data[0]["comment"] == "Not so good"
    assert data[1]["rating"] == "good"
    assert data[1]["comment"] == "Great meal!"
    
    # Test getting reviews for non-existent menu item
    response = client.get(
        "/reviews/999",
        headers={"Authorization": f"Bearer {test_user_token}"}
    )
    assert response.status_code == 404
    assert response.json()["detail"] == "Menu item not found"

def test_get_menu_item_comments(client, test_user_token, test_user, db):
    # Clean up any existing reviews and dining records
    db.query(Review).delete()
    db.query(DiningRecord).delete()
    db.commit()
    
    # Create test data
    menu_item_id = 1
    menu_item_name = "Test Menu Item"
    
    # Create first dining record and review with comment
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
    
    # Create second dining record and review with empty comment
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
        rating="bad",
        comment=""  # Empty comment
    )
    db.add(review2)
    db.commit()
    
    # Test getting comments for the menu item
    response = client.get(
        f"/comments/{menu_item_id}",
        headers={"Authorization": f"Bearer {test_user_token}"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1  # Only one review has a non-empty comment
    
    # Verify the comment data
    assert data[0]["comment"] == "Great meal!"
    assert data[0]["rating"] == "good"
    assert data[0]["user_id"] == test_user.id
    assert data[0]["username"] == test_user.username
    
    # Test getting comments for non-existent menu item
    response = client.get(
        "/comments/999",
        headers={"Authorization": f"Bearer {test_user_token}"}
    )
    assert response.status_code == 404
    assert response.json()["detail"] == "Menu item not found"

def test_get_menu_item_reviews_unauthorized(client):
    # Test accessing reviews endpoint without authentication
    response = client.get("/reviews/1")
    assert response.status_code == 401
    assert response.json()["detail"] == "Not authenticated"

def test_get_menu_item_comments_unauthorized(client):
    # Test accessing comments endpoint without authentication
    response = client.get("/comments/1")
    assert response.status_code == 401
    assert response.json()["detail"] == "Not authenticated"

def test_delete_review(client: TestClient, test_user_token, test_user, db):
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

    # Create review in a new session
    review = Review(
        user_id=test_user.id,
        dining_record_id=dining_record.id,
        rating="good",
        comment="Great meal!"
    )
    db.add(review)
    db.commit()
    db.refresh(review)

    # Get a fresh session for verification
    dining_record_id = dining_record.id
    user_id = test_user.id

    # Test deleting the review
    response = client.delete(
        f"/dining-records/{dining_record_id}/reviews",
        headers={"Authorization": f"Bearer {test_user_token}"}
    )
    assert response.status_code == 204

    # Verify review was deleted using a fresh query
    deleted_review = db.query(Review).filter(
        Review.dining_record_id == dining_record_id,
        Review.user_id == user_id
    ).first()
    assert deleted_review is None, "Review should be deleted after deletion"

def test_delete_review_nonexistent_dining_record(client: TestClient, test_user_token):
    # Test deleting review for non-existent dining record
    response = client.delete(
        "/dining-records/999/reviews",
        headers={"Authorization": f"Bearer {test_user_token}"}
    )
    assert response.status_code == 404
    assert response.json()["detail"] == "Dining record not found"

def test_delete_review_nonexistent_review(client: TestClient, test_user_token, test_user, db):
    # Create a test dining record without a review
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

    # Test deleting non-existent review
    response = client.delete(
        f"/dining-records/{dining_record.id}/reviews",
        headers={"Authorization": f"Bearer {test_user_token}"}
    )
    assert response.status_code == 404
    assert response.json()["detail"] == "Review not found"

def test_delete_review_unauthorized(client: TestClient, test_dining_record_instance):
    # Test deleting review without authentication
    response = client.delete(
        f"/dining-records/{test_dining_record_instance.id}/reviews"
    )
    assert response.status_code == 401
    assert response.json()["detail"] == "Not authenticated"

def test_delete_review_wrong_user(client: TestClient, test_dining_record_instance, test_admin_token):
    # Test deleting review with different user's token
    response = client.delete(
        f"/dining-records/{test_dining_record_instance.id}/reviews",
        headers={"Authorization": f"Bearer {test_admin_token}"}
    )
    assert response.status_code == 404
    assert response.json()["detail"] == "Dining record not found" 