import pytest
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient
from datetime import datetime

def test_send_billing_notifications_success(client: TestClient, mock_admin_user):
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

    # Mock both the user service response and RabbitMQ
    with patch('requests.get') as mock_get, \
         patch('admin_service.rabbitmq.send_notifications_to_users') as mock_send:
        
        # Mock user service response
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = mock_unpaid_users
        
        # Mock RabbitMQ send function
        mock_send.return_value = len(mock_unpaid_users)

        # Make request to admin service
        response = client.post(
            "/billing-notifications/send",
            headers={"Authorization": "Bearer test_token"}
        )

        # Verify response
        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "Billing notifications sent to 2 users"
        assert data["notified_users"] == 2

        # Verify that the request was made to the correct URL with API key
        mock_get.assert_called_once_with(
            "http://user-service:8000/users/unpaid",
            headers={
                "Authorization": "Bearer test_token",
                "X-API-Key": "mealprovider_admin_key"
            }
        )
        
        # Verify that send_notifications_to_users was called with the correct data
        mock_send.assert_called_once_with(mock_unpaid_users)

def test_send_billing_notifications_user_service_error(client: TestClient, mock_admin_user):
    # Mock the requests.get call to user service to return an error
    with patch('requests.get') as mock_get:
        mock_get.return_value.status_code = 500
        mock_get.return_value.json.return_value = {"detail": "Internal server error"}

        # Make request to admin service
        response = client.post(
            "/billing-notifications/send",
            headers={"Authorization": "Bearer test_token"}
        )

        # Verify response
        assert response.status_code == 503
        assert response.json()["detail"] == "User service unavailable"

def test_send_billing_notifications_rabbitmq_error(client: TestClient, mock_admin_user):
    # Mock successful user service response but RabbitMQ error
    mock_unpaid_users = [
        {
            "user_id": 1,
            "user_name": "testuser1",
            "unpaidAmount": 150.0
        }
    ]

    with patch('requests.get') as mock_get, \
         patch('admin_service.rabbitmq.send_notifications_to_users') as mock_send:
        
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = mock_unpaid_users
        mock_send.side_effect = Exception("RabbitMQ error")

        response = client.post(
            "/billing-notifications/send",
            headers={"Authorization": "Bearer test_token"}
        )

        assert response.status_code == 503
        assert response.json()["detail"] == "Message broker unavailable"

def test_send_billing_notifications_unauthorized(client: TestClient):
    # Test without admin token
    response = client.post("/billing-notifications/send")
    assert response.status_code == 401
    assert response.json()["detail"] == "Not authenticated" 