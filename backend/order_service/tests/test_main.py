import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from order_service.main import app
from order_service.models import Base, MenuItem
from order_service.database import get_db

client = TestClient(app)
@pytest.fixture(scope="function")
def client(db):
    # Override the get_db dependency
    def override_get_db():
        try:
            yield db
        finally:
            db.close()
    
    app.dependency_overrides[get_db] = override_get_db
    yield TestClient(app)
    app.dependency_overrides.clear()

SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(scope="session", autouse=True)
def create_tables():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)

@pytest.fixture(scope="function")
def db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.rollback()
        db.close()
"""
@pytest.fixture(scope="function")
def client(db):
    def override_get_db():
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()
"""

def test_create_menu_item(client):

    menu_item_data = {
        "ZH_name": "測試菜單項目 1",
        "EN_name": "Test Menu Item 1",
        "price": 10.0,
        "URL": "http://example.com/image1.png",
        "is_available": True
    }
    response = client.post("/menu-items/", json=menu_item_data)
    assert response.status_code == 200
    data = response.json()
    assert data["ZH_name"] == menu_item_data["ZH_name"]
    assert data["EN_name"] == menu_item_data["EN_name"]
    assert data["price"] == menu_item_data["price"]


def test_get_menu_items(client):
    menu_item_data = {
        "ZH_name": "測試菜單項目 2",
        "EN_name": "Test Menu Item 2",
        "price": 15.0,
        "URL": "http://example.com/image2.png",
        "is_available": True
    }
    client.post("/menu-items/", json=menu_item_data)

    response = client.get("/menu-items/")
    
    items = response.json()

    matched_item = None
    for item in items:
        if item["ZH_name"] == menu_item_data["ZH_name"] and item["EN_name"] == menu_item_data["EN_name"]:
            matched_item = item
            break
    assert response.status_code == 200
    assert matched_item is not None
    assert matched_item["price"] == menu_item_data["price"]




def test_create_order_available(client):
    menu_item_data = {
        "ZH_name": "create_order item available",
        "EN_name": "Test Menu Item Available",
        "price": 10.0,
        "URL": "http://example.com/image_available.png",
        "is_available": True
    }
    client.post("/menu-items/", json=menu_item_data)

    order_data = {
        "user_id": 1,
        "payment_method": "credit_card",
        "items": [
            {
                "menu_item_id": 1,
                "quantity": 2,
                "unit_price": 10.0
            },
            {
                "menu_item_id": 2,
                "quantity": 1,
                "unit_price": 10.0
            }
        ]
    }

    response = client.post("/orders/", json=order_data)

    item = response.json()
    assert response.status_code == 200
    assert item["user_id"] == order_data["user_id"]
    assert item["payment_method"] == order_data["payment_method"]
    assert item["status"] == "pending"
    assert item["payment_status"] == "unpaid"
    assert item["total_amount"] == 35.0 # 2 * 10.0 + 1 * 15.0

def test_create_order_unavailable(client):
    menu_item_data = {
        "ZH_name": "create_order item unavailable",
        "EN_name": "Test Menu Item Unavailable",
        "price": 10.0,
        "URL": "http://example.com/image_unavailable.png",
        "is_available": False
    }
    client.post("/menu-items/", json=menu_item_data)

    order_data = {
        "user_id": 1,
        "payment_method": "credit_card",
        "items": [
            {
                "menu_item_id": 5,
                "quantity": 2,
                "unit_price": 10.0
            }
        ]
    }

    response = client.post("/orders/", json=order_data)
    assert response.status_code == 404

def test_get_order(client):
    response = client.get("/orders/1")
    assert response.status_code == 200

    data = response.json()
    assert data["id"] == 1
    assert data["user_id"] == 1
    assert data["payment_method"] == "credit_card"
    assert data["status"] == "pending"


def test_get_user_orders(client):
    order_item_data_user3_1 = {
        "user_id": 3,
        "payment_method": "credit_card",
        "items": [
            {
                "menu_item_id": 1,
                "quantity": 2,
                "unit_price": 10.0
            },
            {
                "menu_item_id": 2,
                "quantity": 1,
                "unit_price": 10.0
            }
        ]
    }
    
    order_item_data_user3_2 = {
        "user_id": 3,
        "payment_method": "credit_card",
        "items": [
            {
                "menu_item_id": 1,
                "quantity": 2,
                "unit_price": 10.0
            },
            {
                "menu_item_id": 2,
                "quantity": 1,
                "unit_price": 10.0
            }
        ]
    }
    client.post("/orders/", json=order_item_data_user3_1)
    client.post("/orders/", json=order_item_data_user3_2)

    response = client.get("/users/3/orders/")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2

    amount_temp = 0
    for item in data:
        amount_temp += item["total_amount"]
    assert amount_temp == 70.0 # 2 * (2 * 10.0 + 1 * 10.0) = 70.0

def test_update_order_status(client):
    order_status_data = {
        "status": "completed"
    }

    response = client.put("/orders/1/status", params=order_status_data)
    assert response.status_code == 200

    data = response.json()
    assert data["message"] == "Order status updated successfully"

    reponse = client.get("/orders/1")
    data = reponse.json()
    assert data["status"] == "completed"