import pytest
from unittest.mock import patch
from fastapi.testclient import TestClient
from datetime import datetime

def test_get_unpaid_users(client: TestClient, mock_admin_user):
    # Mock the response from user service
    mock_unpaid_users = [
        {
            "user_id": 1,
            "user_name": "testuser1",
            "unpaidAmount": 150.0
        },
        {
            "user_id": 2,
            "user_name": "testuser2",
            "unpaidAmount": 200.0
        }
    ]

    # Mock the requests.get call to user service
    with patch('requests.get') as mock_get:
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = mock_unpaid_users

        # Make request to admin service
        response = client.get(
            "/users/unpaid",
            headers={"Authorization": "Bearer test_token"}
        )

        # Verify response
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2
        
        # Verify first user
        assert data[0]["user_id"] == 1
        assert data[0]["user_name"] == "testuser1"
        assert data[0]["unpaidAmount"] == 150.0
        
        # Verify second user
        assert data[1]["user_id"] == 2
        assert data[1]["user_name"] == "testuser2"
        assert data[1]["unpaidAmount"] == 200.0

        # Verify that the request was made to the correct URL with API key
        mock_get.assert_called_once_with(
            "http://user-service:8000/users/unpaid",
            headers={
                "Authorization": "Bearer test_token",
                "X-API-Key": "mealprovider_admin_key"
            }
        )

def test_get_unpaid_users_user_service_error(client: TestClient, mock_admin_user):
    # Mock the requests.get call to user service to return an error
    with patch('requests.get') as mock_get:
        mock_get.return_value.status_code = 500
        mock_get.return_value.json.return_value = {"detail": "Internal server error"}

        # Make request to admin service
        response = client.get(
            "/users/unpaid",
            headers={"Authorization": "Bearer test_token"}
        )

        # Verify response
        assert response.status_code == 503
        assert response.json()["detail"] == "User service unavailable"

def test_get_unpaid_users_unauthorized(client: TestClient):
    # Test without admin token
    response = client.get("/users/unpaid")
    assert response.status_code == 401
    assert response.json()["detail"] == "Not authenticated" 