# tests/test_main.py
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
import requests_mock
from unittest import mock 


import sys
import os

# 將專案的根目錄 (Meal-Provider/backend/) 加入到 Python 路徑中
# 這樣 Python 才能將 'admin_service' 識別為一個頂級包
# current_file_dir (tests) -> parent_dir (admin_service) -> parent_of_parent_dir (backend)
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))


# 從你的專案導入 app 和其他依賴 (使用絕對導入方式，因為 admin_service 已經在 sys.path 中)
from admin_service.main import app, get_db, verify_admin, USER_SERVICE_URL, ORDER_SERVICE_URL
from admin_service.models import Base, MenuItem, MenuChange
from admin_service.schemas import MenuItemCreate, MenuChangeCreate
# 因為 rabbitmq.py 在 admin_service 包內，所以也要這樣導入
from admin_service.rabbitmq import send_notifications_to_users, send_menu_notification





# 使用 SQLite 記憶體資料庫
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)

TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(scope="session", autouse=True)
def create_tables():
    """
    在所有測試會話開始前創建資料庫表，並在結束後刪除所有表。
    `autouse=True` 表示這個 fixture 會自動應用到所有測試。
    """
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
        db.rollback() # 回滾所有未提交的更改
        db.close()


@pytest.fixture(scope="function")
def client(db):  # db 是共用的 fixture
    def override_get_db():
        yield db  # 不要 close！否則資料在刪除後就查不到

    async def override_verify_admin(token: str = "test-token"):
        return {"id": 1, "username": "admin_test", "role": "admin", "token": token}

    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[verify_admin] = override_verify_admin

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()


# --- Mock 外部服務 Fixture ---
@pytest.fixture(autouse=True)
def mock_external_services_and_rabbitmq():
    """
    自動應用此 fixture，Mock 外部服務的 HTTP 請求和 RabbitMQ 函數。
    """
    with requests_mock.Mocker() as m:
        # Mock User Service 相關請求
        m.get(f"{USER_SERVICE_URL}/users/me", json={"id": 1, "username": "admin_test", "role": "admin"}, status_code=200)
        m.get(f"{USER_SERVICE_URL}/dining-records/", json=[{"id": 1, "user_id": 1, "date": "2023-01-01"}], status_code=200)
        m.get(f"{USER_SERVICE_URL}/users/unpaid", json=[{"id": 1, "username": "user1"}], status_code=200)

        # Mock Order Service 相關請求
        m.get(f"{ORDER_SERVICE_URL}/orders/unpaid", json=[{"user_id": 1, "total_amount": 100.0}], status_code=200)
        m.get(f"{ORDER_SERVICE_URL}/orders/analytics", json={"total_sales": 5000, "item_counts": {"dish1": 100}}, status_code=200)

        # Mock RabbitMQ 發送函數，確保它們不會實際執行發送操作
        with mock.patch('admin_service.main.send_menu_notification') as mock_send_menu_notification, \
             mock.patch('admin_service.main.send_notifications_to_users') as mock_send_notifications_to_users:
            yield m # 繼續執行測試

# --- 菜單相關路由測試 ---
def test_create_menu_item(client, db):
    """測試創建菜單項目。"""
    menu_item_data = {
        "zh_name": "紅燒肉", # 注意這裡的鍵名已經修正為小寫
        "en_name": "Braised Pork",
        "price": 120.5,
        "url": "http://example.com/braised_pork.jpg", # 注意這裡的鍵名已經修正為小寫
        "is_available": True
    }
    response = client.post("/menu-items/", json=menu_item_data)
    assert response.status_code == 201
    created_item = response.json()
    assert created_item["zh_name"] == "紅燒肉"
    assert created_item["en_name"] == "Braised Pork"
    assert created_item["price"] == 120.5
    assert "id" in created_item
    assert "created_at" in created_item
    # --- 軟刪除相關驗證 ---
    assert created_item["is_deleted"] is False # 新增時應為 False
    assert created_item["deleted_at"] is None # 新增時應為 None
    # ----------------------

    # 驗證資料庫中是否存在該項目
    item_in_db = db.query(MenuItem).filter(MenuItem.id == created_item["id"]).first()
    assert item_in_db is not None
    assert item_in_db.zh_name == "紅燒肉"
    assert item_in_db.is_deleted is False # 驗證數據庫中 is_deleted 狀態

    # 驗證 MenuChange 記錄
    change_in_db = db.query(MenuChange).filter(MenuChange.menu_item_id == created_item["id"]).first()
    assert change_in_db is not None
    assert change_in_db.change_type == "add"
    assert change_in_db.old_values is None
    assert change_in_db.new_values["zh_name"] == "紅燒肉"


def test_get_menu_item_by_id(client, db):
    """測試根據 ID 獲取單一菜單項目。"""
    # 先創建一個項目
    menu_item = MenuItem(
        zh_name="雞腿便當", en_name="Chicken Leg Bento", price=95.0, url="url_chicken", is_available=True, is_deleted=False
    )
    db.add(menu_item)
    db.commit()
    db.refresh(menu_item)

    response = client.get(f"/menu-items/{menu_item.id}")
    assert response.status_code == 200
    retrieved_item = response.json()
    assert retrieved_item["id"] == menu_item.id
    assert retrieved_item["zh_name"] == "雞腿便當"
    assert retrieved_item["is_deleted"] is False # 驗證獲取的項目未被刪除

def test_get_menu_item_not_found(client):
    """測試獲取不存在的菜單項目。"""
    response = client.get("/menu-items/999")
    assert response.status_code == 404
    # 更新錯誤訊息以匹配新的路由邏輯，因為可能是不存在或已刪除
    assert response.json()["detail"] == "Menu item not found or has been deleted"



def test_update_menu_item(client, db):
    """測試更新菜單項目並記錄變更。"""
    # 創建一個初始菜單項目
    original_item = MenuItem(
        zh_name="魚香茄子", en_name="Fish Flavored Eggplant", price=150.0, url="url_eggplant", is_available=True, is_deleted=False
    )
    db.add(original_item)
    db.commit()
    db.refresh(original_item)

    # 在還沒呼叫 client 之前先儲存 id
    item_id = original_item.id

    # 準備更新數據
    update_data = {
        "menu_item_id": item_id,
        "change_type": "update",
        "new_values": {
            "price": 160.0,
            "is_available": False
        }
    }

    response = client.put(f"/menu-items/{item_id}/", json=update_data)
    assert response.status_code == 200
    updated_change_record = response.json()

    # 驗證返回的 MenuChange 記錄
    assert updated_change_record["menu_item_id"] == item_id
    assert updated_change_record["change_type"] == "update"
    assert updated_change_record["old_values"]["price"] == 150.0
    assert updated_change_record["new_values"]["price"] == 160.0
    assert updated_change_record["old_values"]["is_available"] is True
    assert updated_change_record["new_values"]["is_available"] is False

    # 驗證資料庫中的 MenuItem 是否已更新
    updated_item_in_db = db.query(MenuItem).filter(MenuItem.id == item_id).first()
    assert updated_item_in_db.price == 160.0
    assert updated_item_in_db.is_available is False
    assert updated_item_in_db.is_deleted is False # 驗證未被軟刪除
    # 驗證資料庫中的 MenuChange 記錄
    change_in_db = db.query(MenuChange).filter(
        MenuChange.menu_item_id == item_id,
        MenuChange.change_type == "update"
    ).order_by(MenuChange.changed_at.desc()).first()
    assert change_in_db is not None
    assert change_in_db.new_values["price"] == 160.0
    assert change_in_db.old_values["price"] == 150.0


def test_update_menu_item_no_changes(client, db):
    """測試更新菜單項目但沒有任何變更。"""
    original_item = MenuItem(
        zh_name="測試菜品", en_name="Test Dish", price=100.0, url="url_test", is_available=True, is_deleted=False
    )
    db.add(original_item)
    db.commit()
    db.refresh(original_item)

    # 傳遞與資料庫中完全相同的值
    update_data = {
        "menu_item_id": original_item.id,
        "change_type": "update",
        "new_values": {
            "zh_name": "測試菜品",
            "en_name": "Test Dish",
            "price": 100.0,
            "url": "url_test",
            "is_available": True
        }
    }
    response = client.put(f"/menu-items/{original_item.id}/", json=update_data)
    assert response.status_code == 400
    assert response.json()["detail"] == "No changes detected for menu item."

# --- 將硬刪除測試改為軟刪除測試 ---
def test_soft_delete_menu_item(client, db):
    """測試軟刪除菜單項目。"""
    menu_item_to_delete = MenuItem(
        zh_name="待軟刪除菜品", en_name="Dish to soft delete", price=50.0, url="url_delete", is_available=True, is_deleted=False
    )
    db.add(menu_item_to_delete)
    db.commit()
    db.refresh(menu_item_to_delete)

    # 調用新的軟刪除路由
    response = client.delete(f"/menu-items/{menu_item_to_delete.id}") # 路由已改為 /menu-items/{id}
    assert response.status_code == 200
    assert response.json()["message"] == f"Menu item with id {menu_item_to_delete.id} soft deleted successfully and change recorded."

    # 驗證菜單項目是否在資料庫中但被標記為 deleted
    deleted_item = db.query(MenuItem).filter(MenuItem.id == menu_item_to_delete.id).first()
    assert deleted_item is not None # 軟刪除後項目依然存在
    assert deleted_item.is_deleted is True # is_deleted 應為 True
    assert deleted_item.deleted_at is not None # deleted_at 應有值

    # 驗證 MenuChange 記錄
    change_record = db.query(MenuChange).filter(MenuChange.menu_item_id == menu_item_to_delete.id).order_by(MenuChange.changed_at.desc()).first()
    assert change_record is not None
    assert change_record.change_type == "soft_remove" # 變更類型應為 "soft_remove"
    assert change_record.old_values["is_deleted"] is False # 舊的 is_deleted 狀態
    assert change_record.new_values["is_deleted"] is True # 新的 is_deleted 狀態
    assert change_record.new_values["deleted_at"] is not None # 新的 deleted_at 應有值


def test_soft_delete_menu_item_not_found(client):
    """測試軟刪除不存在或已刪除的菜單項目。"""
    response = client.delete("/menu-items/999") # 路由已改
    assert response.status_code == 404
    assert response.json()["detail"] == "Menu item not found or already deleted"

def test_soft_delete_already_deleted_menu_item(client, db):
    """測試嘗試再次軟刪除已軟刪除的菜單項目。"""
    already_deleted_item = MenuItem(
        zh_name="已刪除菜品", en_name="Already Deleted Dish", price=60.0, url="url_already_deleted", is_available=True, is_deleted=True
    )
    db.add(already_deleted_item)
    db.commit()
    db.refresh(already_deleted_item)

    response = client.delete(f"/menu-items/{already_deleted_item.id}")
    assert response.status_code == 404
    assert response.json()["detail"] == "Menu item not found or already deleted"



def test_toggle_menu_item_availability(client, db):
    """測試切換菜單項目上架/下架狀態。"""
    menu_item = MenuItem(
        zh_name="可切換菜品", en_name="Toggle Dish", price=75.0, url="url_toggle", is_available=True, is_deleted=False
    )
    db.add(menu_item)
    db.commit()
    db.refresh(menu_item)

    # 第一次切換：從 True 到 False
    response = client.put(f"/menu-items/{menu_item.id}/toggle-availability")
    assert response.status_code == 200
    updated_item = response.json()
    assert updated_item["is_available"] is False
    assert updated_item["is_deleted"] is False # 驗證軟刪除狀態未改變

    # 驗證資料庫中的狀態
    item_in_db = db.query(MenuItem).filter(MenuItem.id == menu_item.id).first()
    assert item_in_db.is_available is False
    assert item_in_db.is_deleted is False # 驗證軟刪除狀態未改變

    # 驗證 MenuChange 記錄 (第一次切換)
    change_record_1 = db.query(MenuChange).filter(
        MenuChange.menu_item_id == menu_item.id,
        MenuChange.change_type == "toggle_availability"
    ).order_by(MenuChange.changed_at.desc()).first()
    assert change_record_1 is not None
    assert change_record_1.old_values["is_available"] is True
    assert change_record_1.new_values["is_available"] is False

    # 第二次切換：從 False 到 True
    response = client.put(f"/menu-items/{menu_item.id}/toggle-availability")
    assert response.status_code == 200
    updated_item = response.json()
    assert updated_item["is_available"] is True
    assert updated_item["is_deleted"] is False

    # 驗證資料庫中的狀態
    item_in_db = db.query(MenuItem).filter(MenuItem.id == menu_item.id).first()
    assert item_in_db.is_available is True
    assert item_in_db.is_deleted is False

    # 驗證 MenuChange 記錄 (第二次切換)
    change_record_2 = db.query(MenuChange).filter(
        MenuChange.menu_item_id == menu_item.id,
        MenuChange.change_type == "toggle_availability"
    ).order_by(MenuChange.changed_at.desc()).first()
    assert change_record_2 is not None
    assert change_record_2.old_values["is_available"] is False
    assert change_record_2.new_values["is_available"] is True

def test_toggle_menu_item_availability_not_found(client):
    """測試切換不存在菜單項目狀態。"""
    response = client.put("/menu-items/999/toggle-availability")
    assert response.status_code == 404
    assert response.json()["detail"] == "Menu item not found or has been deleted"

def test_toggle_availability_of_deleted_menu_item(client, db):
    """測試切換已軟刪除菜單項目狀態，應返回 404。"""
    deleted_item = MenuItem(
        zh_name="已刪除菜品", en_name="Deleted Dish", price=100.0, url="url_deleted", is_available=True, is_deleted=True
    )
    db.add(deleted_item)
    db.commit()
    db.refresh(deleted_item)

    response = client.put(f"/menu-items/{deleted_item.id}/toggle-availability")
    assert response.status_code == 404
    assert response.json()["detail"] == "Menu item not found or has been deleted"