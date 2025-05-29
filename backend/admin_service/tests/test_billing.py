# tests/test_billing.py
import pytest
from fastapi.testclient import TestClient
import requests_mock
from unittest import mock
import pika

import sys
import os

# Add project root to Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from admin_service.main import app, get_db, verify_admin, USER_SERVICE_URL
from admin_service.rabbitmq import send_notifications_to_users

# --- Test Fixtures ---
@pytest.fixture(scope="function")
def client():
    # Mock verify_admin function
    async def override_verify_admin(token: str = "test-token"):
        return {"id": 1, "username": "admin_test", "role": "admin", "token": token}

    app.dependency_overrides[verify_admin] = override_verify_admin

    with TestClient(app) as test_client:
        yield test_client
    
    # Clear dependency overrides
    app.dependency_overrides.clear()

@pytest.fixture(autouse=True)
def mock_external_services_and_rabbitmq():
    """
    Automatically applied fixture to mock external service HTTP requests and RabbitMQ functions.
    """
    with requests_mock.Mocker() as m:
        # Mock User Service related requests
        m.get(f"{USER_SERVICE_URL}/users/me", json={"id": 1, "username": "admin_test", "role": "admin"}, status_code=200)
        m.get(f"{USER_SERVICE_URL}/dining-records/", json=[{"id": 1, "user_id": 1, "date": "2023-01-01"}], status_code=200)
        m.get(f"{USER_SERVICE_URL}/users/unpaid", json=[{"id": 1, "username": "user1"}], status_code=200)

        # Mock RabbitMQ sending functions
        with mock.patch('admin_service.main.send_notifications_to_users', return_value=1) as mock_send_notifications:
            yield m

# --- Test Cases ---

def test_get_all_dining_records(client, mock_external_services_and_rabbitmq):
    """Test getting all dining records."""
    response = client.get("/dining-records/")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0
    assert "id" in data[0]
    assert "user_id" in data[0]
    assert "date" in data[0]

def test_get_all_dining_records_service_error(client, mock_external_services_and_rabbitmq):
    """Test getting dining records when user service returns an error."""
    # Override the mock to simulate user service error
    mock_external_services_and_rabbitmq.get(
        f"{USER_SERVICE_URL}/dining-records/",
        status_code=500
    )
    
    response = client.get("/dining-records/")
    assert response.status_code == 500
    assert "Failed to fetch dining records from user service" in response.json()["detail"]

def test_get_unpaid_users(client, mock_external_services_and_rabbitmq):
    """Test getting all unpaid users."""
    response = client.get("/users/unpaid")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0
    assert "id" in data[0]
    assert "username" in data[0]

def test_get_unpaid_users_service_error(client, mock_external_services_and_rabbitmq):
    """Test getting unpaid users when user service returns an error."""
    # Override the mock to simulate user service error
    mock_external_services_and_rabbitmq.get(
        f"{USER_SERVICE_URL}/users/unpaid",
        status_code=500
    )
    
    response = client.get("/users/unpaid")
    assert response.status_code == 500
    assert "Failed to fetch unpaid users from user service" in response.json()["detail"]

def test_send_billing_notifications(client, mock_external_services_and_rabbitmq):
    """Test sending billing notifications to unpaid users."""
    # Mock the send_notifications_to_users function to return 1 (one user notified)
    with mock.patch('admin_service.main.send_notifications_to_users', return_value=1):
        response = client.post("/billing-notifications/send")
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "notified_users" in data
        assert isinstance(data["notified_users"], int)
        assert data["notified_users"] == 1

def test_send_billing_notifications_no_unpaid_users(client, mock_external_services_and_rabbitmq):
    """Test sending billing notifications when there are no unpaid users."""
    # Override the mock for this specific test
    mock_external_services_and_rabbitmq.get(
        f"{USER_SERVICE_URL}/users/unpaid",
        json=[],
        status_code=200
    )
    
    # Mock the send_notifications_to_users function to return 0 (no users notified)
    with mock.patch('admin_service.main.send_notifications_to_users', return_value=0):
        response = client.post("/billing-notifications/send")
        assert response.status_code == 200
        data = response.json()
        assert data["notified_users"] == 0

def test_send_billing_notifications_user_service_error(client, mock_external_services_and_rabbitmq):
    """Test sending billing notifications when user service returns an error."""
    # Override the mock to simulate user service error
    mock_external_services_and_rabbitmq.get(
        f"{USER_SERVICE_URL}/users/unpaid",
        status_code=500
    )
    
    response = client.post("/billing-notifications/send")
    assert response.status_code == 500
    assert "Failed to fetch unpaid users from user service" in response.json()["detail"]

def test_send_billing_notifications_rabbitmq_error(client, mock_external_services_and_rabbitmq):
    """Test sending billing notifications when RabbitMQ service is unavailable."""
    # Mock RabbitMQ error by raising pika.exceptions.AMQPConnectionError
    with mock.patch('admin_service.main.send_notifications_to_users', 
                   side_effect=pika.exceptions.AMQPConnectionError("Connection refused")):
        response = client.post("/billing-notifications/send")
        assert response.status_code == 503
        assert "Message broker unavailable" in response.json()["detail"] 