import pytest
from unittest.mock import patch
from fastapi.testclient import TestClient
from datetime import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from admin_service.main import app, get_db
from admin_service.models import Base

# Create test database
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def override_get_db():
    connection = engine.connect()
    db = TestingSessionLocal(bind=connection)
    try:
        yield db
    finally:
        db.close()
        connection.close()

# Override the get_db dependency
app.dependency_overrides[get_db] = override_get_db

@pytest.fixture(name="client")
def client_fixture():
    Base.metadata.create_all(bind=engine)
    with TestClient(app) as c:
        yield c
    Base.metadata.drop_all(bind=engine)

@pytest.fixture
def mock_admin_user():
    with patch('requests.get') as mock_requests_get:
        mock_requests_get.return_value.status_code = 200
        mock_requests_get.return_value.json.return_value = {
            "id": 1,
            "role": "admin",
            "email": "admin_test@example.com",
            "username": "test_admin"
        }
        yield

def test_get_all_dining_records(client: TestClient, mock_admin_user):
    # Mock the response from user service
    mock_dining_records = [
        {
            "id": 1,
            "user_id": 1,
            "order_id": 1,
            "menu_item_id": 1,
            "menu_item_name": "Test Menu Item 1",
            "total_amount": 100.0,
            "payment_status": "paid",
            "created_at": datetime.now().isoformat()
        },
        {
            "id": 2,
            "user_id": 1,
            "order_id": 2,
            "menu_item_id": 2,
            "menu_item_name": "Test Menu Item 2",
            "total_amount": 200.0,
            "payment_status": "unpaid",
            "created_at": datetime.now().isoformat()
        }
    ]

    # Mock the requests.get call to user service
    with patch('requests.get') as mock_get:
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = mock_dining_records

        # Make request to admin service
        response = client.get(
            "/dining-records/",
            headers={"Authorization": "Bearer test_token"}
        )

        # Verify response
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2
        
        # Verify first record
        assert data[0]["id"] == 1
        assert data[0]["menu_item_name"] == "Test Menu Item 1"
        assert data[0]["payment_status"] == "paid"
        assert data[0]["total_amount"] == 100.0
        
        # Verify second record
        assert data[1]["id"] == 2
        assert data[1]["menu_item_name"] == "Test Menu Item 2"
        assert data[1]["payment_status"] == "unpaid"
        assert data[1]["total_amount"] == 200.0

        # Verify that the request was made to the correct URL
        mock_get.assert_called_once_with(
            "http://user-service:8000/dining-records/",
            headers={"Authorization": "Bearer test_token"}
        )

def test_get_all_dining_records_user_service_error(client: TestClient, mock_admin_user):
    # Mock the requests.get call to user service to return an error
    with patch('requests.get') as mock_get:
        mock_get.return_value.status_code = 500
        mock_get.return_value.json.return_value = {"detail": "Internal server error"}

        # Make request to admin service
        response = client.get(
            "/dining-records/",
            headers={"Authorization": "Bearer test_token"}
        )

        # Verify response
        assert response.status_code == 503
        assert response.json()["detail"] == "User service unavailable"

def test_get_all_dining_records_unauthorized(client: TestClient):
    # Test without admin token
    response = client.get("/dining-records/")
    assert response.status_code == 401
    assert response.json()["detail"] == "Not authenticated" 