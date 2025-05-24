import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

# 確保這裡導入的是 admin_service 的 app、models 和 database 模組
# 調整 sys.path 以便正確導入
import sys
import os

# 確保此路徑指向你的專案根目錄 (backend 目錄)
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

# 正確導入 Admin Service 的模組
from admin_service.main import app
from admin_service.models import Base, MenuItem, MenuItemTranslation, MenuChange, BillingNotification, Analytics
from admin_service.database import get_db as original_get_db # 導入原始的 get_db 函數，以便覆寫它
# 如果 admin_service.main 中有 verify_admin 依賴，也需要導入
from admin_service.main import verify_admin # 假設 verify_admin 在 main.py 中

# 確保導入 schemas
from admin_service.schemas import MenuItemCreate, MenuChangeCreate


# ====================================================================
# 1. 設置測試資料庫 (使用 SQLite in-memory)
# ====================================================================
# 注意：這裡的 engine 和 TestingSessionLocal 是專為測試準備的
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"
test_engine = create_engine( # 改名為 test_engine 區分
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)


# ====================================================================
# 2. Pytest Fixtures
# ====================================================================

@pytest.fixture(scope="session", autouse=True)
def setup_test_db():
    """
    會話級別的 fixture，在所有測試運行前創建表，在所有測試運行後刪除表。
    確保測試資料庫是乾淨的。
    """
    print("\nSetting up Admin Service test database...")
    # 使用測試專用的 engine 來創建和刪除表
    Base.metadata.create_all(bind=test_engine)
    yield
    Base.metadata.drop_all(bind=test_engine)
    print("Tearing down Admin Service test database.")

@pytest.fixture(scope="function")
def db_session():
    """
    函數級別的 fixture，為每個測試提供一個獨立的資料庫會話。
    測試結束後會回滾所有更改並關閉會話，確保測試之間不互相影響。
    """
    # 使用測試專用的 engine 來獲取連接和會話
    connection = test_engine.connect()
    transaction = connection.begin()
    session = TestingSessionLocal(bind=connection)
    yield session
    session.close()
    transaction.rollback() # 回滾所有更改
    connection.close()

@pytest.fixture(scope="function")
def client(db_session):
    """
    函數級別的 fixture，提供一個 TestClient 實例，
    並覆蓋 Admin Service 的資料庫依賴，使其使用測試資料庫。
    """
    # 覆寫 get_db 依賴，使用測試資料庫會話
    def override_get_db():
        yield db_session

    # 模擬 verify_admin 依賴，直接返回管理員資料
    def override_verify_admin():
        return {"id": 1, "role": "admin"}

    # 將原始的 get_db 替換為我們的 override_get_db
    app.dependency_overrides[original_get_db] = override_get_db
    app.dependency_overrides[verify_admin] = override_verify_admin # 覆寫 verify_admin

    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear() # 清除所有依賴覆寫

# ====================================================================
# 3. 測試數據 (可以根據需要定義更多)
# ====================================================================

@pytest.fixture
def sample_menu_item_data():
    return {
        "name": "測試菜單 A",
        "description": "這是一個測試用的菜單項目",
        "price": 100.0,
        "category": "主食"
    }

@pytest.fixture
def sample_menu_item_data_b():
    return {
        "name": "測試菜單 B",
        "description": "用於驗證修改菜單",
        "price": 139.99,
        "category": "測試"
    }

@pytest.fixture
def sample_menu_item_data_delete():
    return {
        "name": "測試刪除菜單",
        "description": "用於驗證刪除功能",
        "price": 99.99,
        "category": "測試"
    }

# ====================================================================
# 4. Pytest 測試函數
# ====================================================================

def test_create_menu_item(client, sample_menu_item_data):
    """測試新增單筆菜單項目的功能。"""
    response = client.post("/menu-items/", json=sample_menu_item_data)
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == sample_menu_item_data["name"]
    assert data["description"] == sample_menu_item_data["description"]
    assert data["price"] == sample_menu_item_data["price"]
    assert data["category"] == sample_menu_item_data["category"]
    assert "id" in data
    assert len(data["translations"]) > 0

def test_get_all_menu_items(client, sample_menu_item_data):
    """測試取得所有菜單項目的功能。"""
    client.post("/menu-items/", json=sample_menu_item_data) # 確保有數據

    response = client.get("/menu-items/")
    assert response.status_code == 200
    items = response.json()
    assert isinstance(items, list)
    assert len(items) > 0
    found = False
    for item in items:
        if item["name"] == sample_menu_item_data["name"]:
            found = True
            assert item["description"] == sample_menu_item_data["description"]
            assert item["price"] == sample_menu_item_data["price"]
            assert item["category"] == sample_menu_item_data["category"]
            break
    assert found, "新增的菜單項目未在所有菜單列表中找到"

def test_get_menu_item_by_id(client, sample_menu_item_data):
    """測試取得單筆菜單項目的功能 (根據 ID)。"""
    create_response = client.post("/menu-items/", json=sample_menu_item_data)
    created_item_id = create_response.json()["id"]

    response = client.get(f"/menu-items/{created_item_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == created_item_id
    assert data["name"] == sample_menu_item_data["name"]

def test_update_menu_item(client, sample_menu_item_data_b):
    """測試修改菜單項目的功能 (通過 /menu-changes/ 端點)。"""
    create_response = client.post("/menu-items/", json=sample_menu_item_data_b)
    initial_item = create_response.json()
    item_id = initial_item["id"]

    update_payload = {
        "name": "修改後的測試菜單 B",
        "price": 149.99
    }
    change_payload = MenuChangeCreate(
        menu_item_id=item_id,
        change_type="update",
        new_values=update_payload
    )

    response = client.post("/menu-changes/", json=change_payload.dict())
    assert response.status_code == 200
    data = response.json()
    assert data["menu_item_id"] == item_id
    assert data["change_type"] == "update"
    assert data["changed_fields"]["name"] == update_payload["name"]
    assert data["changed_fields"]["price"] == update_payload["price"]

    get_response = client.get(f"/menu-items/{item_id}")
    assert get_response.status_code == 200
    updated_item = get_response.json()
    assert updated_item["name"] == update_payload["name"]
    assert updated_item["price"] == update_payload["price"]

def test_delete_menu_item(client, sample_menu_item_data_delete):
    """測試刪除單筆菜單項目的功能。"""
    create_response = client.post("/menu-items/", json=sample_menu_item_data_delete)
    created_item_id = create_response.json()["id"]

    delete_response = client.delete(f"/menu-items/{created_item_id}")
    assert delete_response.status_code == 200
    assert delete_response.json()["message"] == f"Menu item with id {created_item_id} deleted successfully"

    get_response_after_delete = client.get(f"/menu-items/{created_item_id}")
    assert get_response_after_delete.status_code == 404