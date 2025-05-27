import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from order_service.main import app, router
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

def test_analytics(client):
    menu_item_data_1 = {
        "ZH_name": "測試菜單項目 1",
        "EN_name": "Test Menu Item 1",
        "price": 10.0,
        "URL": "http://example.com/image1.png",
        "is_available": True
    }
    response = client.post("/menu-items/", json=menu_item_data_1)
    assert response.status_code == 200

    menu_item_data_2 = {
        "ZH_name": "測試菜單項目 2",
        "EN_name": "Test Menu Item 2",
        "price": 10.0,
        "URL": "http://example.com/image2.png",
        "is_available": True
    }
    response = client.post("/menu-items/", json=menu_item_data_2)
    assert response.status_code == 200

    order_item_data_user3_2 = {
        "user_id": 3,
        "payment_method": "credit_card",
        "status": "completed", 
        "items": [
            {
                "menu_item_id": 1,
                "quantity": 2,
                "unit_price": 10.0
            }
        ]
    }
    client.post("/orders/", json=order_item_data_user3_2)

    response = client.get("/api/analytics", params={"report_type": "order_trends", "report_period": "weekly"})

    # assert response.status_code == 200
    #print(response.json())
    print("Response", response)
    csv_data = response.content.decode("utf-8")
    import pandas as pd
    from io import StringIO
    df = pd.read_csv(StringIO(csv_data))
    print("DataFrame", df)
    assert not df.empty
    """
    item_id,item_name,quantity,income
    1,Test Menu Item 1,2,20.00
    """
    assert df["item_id"].tolist() == [1]
    assert df["item_name"].tolist() == ["Test Menu Item 1"]
    assert df["quantity"].tolist() == [2]
    assert df["income"].tolist() == [20.0]
    