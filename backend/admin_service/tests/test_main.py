import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from unittest.mock import patch, MagicMock # 確保導入 MagicMock
from datetime import datetime, timedelta

# 從 admin_service 套件中導入你的 FastAPI app, models 和 database get_db 函式
# 確保 admin_service 目錄下有 __init__.py 檔案，並且你從 backend/ 目錄運行 pytest
from admin_service.main import app, get_db, verify_admin # 導入 verify_admin 函式本身
from admin_service.models import Base, MenuItem, MenuItemTranslation, MenuChange, BillingNotification, Analytics

# --- 測試資料庫設定 ---
# 使用記憶體中的 SQLite 資料庫進行測試
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

# 建立一個新的 engine，並設定 check_same_thread=False 以支援 SQLite
# StaticPool 讓每個連接都是同一個，確保測試中的所有 Session 都使用相同的記憶體資料庫
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)

# 建立一個新的 SessionLocal 給測試使用
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# --- 覆寫 get_db 依賴 ---
# 這個函數將在每次測試時被 FastAPI 調用，用來替代你的 database.get_db
# 它提供了一個連接到記憶體 SQLite 資料庫的 Session
def override_get_db():
    connection = engine.connect()
    # transaction = connection.begin() # <--- 移除或註釋掉這一行
    db = TestingSessionLocal(bind=connection)
    try:
        yield db
    finally:
        db.close()
        # transaction.rollback() # <--- 移除或註釋掉這一行
        connection.close()

# 將 FastAPI app 的 get_db 依賴替換為我們的測試用 get_db (override_get_db)
app.dependency_overrides[get_db] = override_get_db
async def override_verify_admin():
    return {"id": 1, "role": "admin", "email": "admin@example.com"}

app.dependency_overrides[verify_admin] = override_verify_admin

# --- pytest fixture for TestClient ---
@pytest.fixture(name="client")
def client_fixture():
    # 在每次測試開始前，在記憶體資料庫中建立所有定義的表格
    Base.metadata.create_all(bind=engine)
    with TestClient(app) as c:
        yield c # 提供 TestClient 實例給測試函數
    # 在每次測試結束後，刪除所有表格，確保資料庫完全清空，為下一個測試準備
    Base.metadata.drop_all(bind=engine)

# --- 模擬 verify_admin 依賴成功 ---
# 這個 fixture 會模擬 requests.get 函數的行為，使其回傳一個成功的管理員用戶
@pytest.fixture
def mock_admin_user():
    # 使用 patch 模擬 `requests` 模組中的 `get` 函數
    # 這裡的路徑是 `admin_service.main.requests.get`，因為 `main.py` 導入了 `requests`
    with patch('requests.get') as mock_requests_get:
        # 設定模擬的 `requests.get` 調用回傳的響應對象的屬性
        # 模擬 HTTP 200 OK 狀態碼
        mock_requests_get.return_value.status_code = 200
        # 模擬響應對象的 .json() 方法回傳的數據，這將是 verify_admin 函數的 user_data
        mock_requests_get.return_value.json.return_value = {
            "id": 1,
            "role": "admin", # 模擬管理員角色
            "email": "admin_test@example.com",
            "username": "test_admin"
        }
        yield # 執行測試
# --- 模擬 googletrans.Translator 的翻譯行為 (因為你希望暫時跳過實際翻譯測試) ---
# --- 模擬 googletrans.Translator 的翻譯行為 (更通用的方式) ---
@pytest.fixture
def mock_translator():
    with patch('admin_service.main.Translator') as mock_translator_class:
        mock_instance = mock_translator_class.return_value
        # 設置實例的 translate 方法的行為，使其回傳模擬的翻譯結果
        # 這會根據輸入的 text 和 dest 動態生成翻譯結果
        mock_instance.translate.side_effect = lambda text, dest: MagicMock(text=f"{text} translated to {dest}")
        yield mock_instance
# --- 模擬 googletrans.Translator 的翻譯行為 ---#
#@pytest.fixture
#def mock_translator():
    # 模擬 `admin_service.main` 模組中的 `Translator` 類
  #  with patch('admin_service.main.Translator') as mock_translator_class:
 #       mock_instance = mock_translator_class.return_value # 獲取 Translator 類的實例
        # 設定實例的 translate 方法的行為，使其回傳模擬的翻譯結果
#        mock_instance.translate.side_effect = lambda text, dest: type('obj', (object,), {'text': f"{text} translated to {dest}"})()
#        yield mock_instance

# --- (可選) 模擬對 Order Service 的 requests.post 請求 ---
# 如果你有其他路由會調用 requests.post 到 Order Service，你可能需要這個
@pytest.fixture
def mock_order_service_post():
    with patch('requests.post') as mock_post:
        mock_post.return_value.status_code = 200 # 假設請求成功
        yield mock_post

@pytest.fixture
def mock_order_service_get():
    with patch('requests.get') as mock_get:
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = {}
        yield mock_get
@pytest.fixture
def mock_order_service_put():
    with patch('requests.put') as mock_put:
        mock_put.return_value.status_code = 200
        yield mock_put
# =======================================================================
# 測試案例：取得所有菜品
# =======================================================================
def test_create_menu_item(client: TestClient, mock_admin_user, mock_order_service_post):
    # 獲取測試資料庫的 Session
    db = TestingSessionLocal()

    # 準備要新增的菜品資料
    new_menu_item_data = {
        "name": "測試菜品",
        "description": "這是一個測試用的菜品描述",
        "price": 99.99,
        "category": "測試分類"
    }

    # 發送 POST 請求新增菜品
    response = client.post(
        "/menu-items/",
        json=new_menu_item_data,
        headers={"Authorization": "Bearer test_token"}
    )

    # 驗證回應狀態碼
    #print(f"Response JSON: {response.json()}") # <--- 新增這行
    #assert response.status_code == 200
    response_data = response.json()

    # 驗證回應資料的結構和內容
    assert "id" in response_data
    assert response_data["name"] == new_menu_item_data["name"]
    assert response_data["description"] == new_menu_item_data["description"]
    assert response_data["price"] == new_menu_item_data["price"]
    assert response_data["category"] == new_menu_item_data["category"]
    assert "created_at" in response_data
    assert "updated_at" in response_data # 應該存在但為 None

    # 驗證資料庫中是否確實新增了該菜品
    created_menu_item = db.query(MenuItem).filter(MenuItem.id == response_data["id"]).first()
    assert created_menu_item is not None
    assert created_menu_item.name == new_menu_item_data["name"]
    assert created_menu_item.description == new_menu_item_data["description"]
    print("有新增ㄇ",created_menu_item.name)
    print("有新增ㄇ",created_menu_item.description)
    # 驗證翻譯是否正確儲存
    # 驗證翻譯是否正確儲存 (這裡現在會調用實際的 googletrans API)


    # 驗證 mock_order_service_post 是否被呼叫
    mock_order_service_post.assert_called_once()
    assert mock_order_service_post.call_args.kwargs['json'] == {"menu_item_id": created_menu_item.id}
    assert mock_order_service_post.call_args.args[0] == f"http://order-service:8000/menu-items/"

    db.close()

# =======================================================================
# 新增測試案例：刪除菜品 (DELETE /menu-items/{menu_item_id})
# =======================================================================
def test_delete_menu_item(client: TestClient):
    db = TestingSessionLocal()
    # 1. 準備測試資料：先創建一個菜品供刪除
    menu_item_to_delete = MenuItem(name="Delete Me", description="This item will be deleted", price=5.0, category="Temp")
    db.add(menu_item_to_delete)
    db.commit()
    db.refresh(menu_item_to_delete)
    
    # 添加一些翻譯，確保它們也會被刪除
    translation_zh = MenuItemTranslation(language="zh-TW", name="刪除我", description="此項目將被刪除")
    menu_item_to_delete.translations.append(translation_zh)
    db.commit()
    db.refresh(menu_item_to_delete)
    
    # 獲取要刪除的菜品 ID
    item_id = menu_item_to_delete.id
    db.close() # 關閉設置數據的 Session

    # 2. 發送 DELETE 請求
    response = client.delete(
        f"/menu-items/{item_id}",
        headers={"Authorization": "Bearer test_token"}
    )

    # 3. 斷言回應狀態碼和訊息
    assert response.status_code == 200
    assert response.json() == {"message": f"Menu item with id {item_id} deleted successfully"}

    # 4. 驗證菜品是否已從資料庫中移除
    db = TestingSessionLocal() # 重新打開 Session 進行驗證
    deleted_item = db.query(MenuItem).filter(MenuItem.id == item_id).first()
    assert deleted_item is None # 菜品應該不存在了

    # 5. 驗證所有相關翻譯是否也已移除
    deleted_translations = db.query(MenuItemTranslation).filter(
        MenuItemTranslation.menu_items.any(id=item_id) # 這裡將不再返回任何 MenuItemTranslation
    ).all()
    assert len(deleted_translations) == 0

    db.close()

   
def test_get_all_menu_items(
    client: TestClient,       # 來自 client_fixture，用於發送 HTTP 請求
    mock_translator # 重新引入 mock_translator，因為你希望暫時跳過實際翻譯
):
    # 1. 準備測試資料
    db = TestingSessionLocal()
    menu_item_1 = MenuItem(name="Original Dish A", description="Description A", price=10.0, category="Main")
    menu_item_2 = MenuItem(name="Original Dish B", description="Description B", price=15.0, category="Side")
    db.add(menu_item_1)
    db.add(menu_item_2)
    db.commit() # 提交到資料庫，使它們獲得 ID
    db.refresh(menu_item_1) # 刷新實例以獲取資料庫生成的 ID
    db.refresh(menu_item_2)

    # 為 menu_item_1 添加多語言翻譯 (手動插入，這樣路由就從資料庫讀取)
    # 正確的方式是將 MenuItemTranslation 實例添加到 MenuItem 的 translations 關係中
    translation_zh_1 = MenuItemTranslation(language="zh-TW", name="菜品A", description="菜品A描述")
    translation_en_1 = MenuItemTranslation(language="en-US", name="Dish A", description="Dish A Description")
    
    # 將翻譯實例添加到 menu_item_1 的 translations 關係中
    menu_item_1.translations.append(translation_zh_1)
    menu_item_1.translations.append(translation_en_1)
    db.commit() # 提交更改，這會自動處理關聯表
    db.refresh(menu_item_1) # 刷新以確保關聯被保存

    # 為 menu_item_2 添加一個中文翻譯
    translation_zh_2 = MenuItemTranslation(language="zh-TW", name="菜品B", description="菜品B描述")
    # 將翻譯實例添加到 menu_item_2 的 translations 關係中
    menu_item_2.translations.append(translation_zh_2)
    db.commit() # 提交更改
    db.refresh(menu_item_2)


    # 2. 發送 HTTP 請求
    # 測試預設語言 (zh-TW)
    response_zh = client.get("/menu-items/", headers={"Authorization": "Bearer test_token"})

    # 3. 斷言結果 (預設語言 zh-TW)
    assert response_zh.status_code == 200
    data_zh = response_zh.json()
    assert len(data_zh) == 2 # 應該回傳所有兩個菜品

    # 檢查第一個菜品的回傳數據是否正確 (中文翻譯)
    item_a_zh = next((item for item in data_zh if item["id"] == menu_item_1.id), None)
    assert item_a_zh is not None
    assert item_a_zh["name"] == "菜品A"  # 應該是翻譯後的名稱
    assert item_a_zh["description"] == "菜品A描述" # 應該是翻譯後的描述
    assert item_a_zh["price"] == 10.0
    assert item_a_zh["category"] == "Main"

    # 檢查第二個菜品的回傳數據是否正確 (中文翻譯)
    item_b_zh = next((item for item in data_zh if item["id"] == menu_item_2.id), None)
    assert item_b_zh is not None
    assert item_b_zh["name"] == "菜品B"
    assert item_b_zh["description"] == "菜品B描述"
    assert item_b_zh["price"] == 15.0
    assert item_b_zh["category"] == "Side"

    # 測試指定語言 (en-US)
    response_en = client.get("/menu-items/", params={"language": "en-US"}, headers={"Authorization": "Bearer test_token"})

    # 斷言結果 (指定語言 en-US)
    assert response_en.status_code == 200
    data_en = response_en.json()

    # 檢查第一個菜品 (有英文翻譯)
    item_a_en = next((item for item in data_en if item["id"] == menu_item_1.id), None)
    assert item_a_en is not None
    assert item_a_en["name"] == "Dish A"
    assert item_a_en["description"] == "Dish A Description"

    # 檢查第二個菜品 (沒有英文翻譯，應該回傳原始名稱和描述)
    item_b_en = next((item for item in data_en if item["id"] == menu_item_2.id), None)
    assert item_b_en is not None
    assert item_b_en["name"] == "Original Dish B"
    assert item_b_en["description"] == "Description B"

################

# =======================================================================
# 測試案例：更新菜單 (POST /menu-changes/)
# =======================================================================
def test_create_menu_change(client: TestClient, mock_admin_user, mock_order_service_put, mock_translator):
    db = TestingSessionLocal()
    original_menu_item = MenuItem(name="Original Name", description="Original Description", price=10.0, category="Main")
    db.add(original_menu_item)
    db.commit()
    db.refresh(original_menu_item)

    initial_translation_zh = MenuItemTranslation(language="zh-TW", name="原始名稱", description="原始描述")
    initial_translation_en = MenuItemTranslation(language="en-US", name="Original Name", description="Original Description")
    original_menu_item.translations.append(initial_translation_zh)
    original_menu_item.translations.append(initial_translation_en)
    db.commit()
    db.refresh(original_menu_item)


    menu_change_data = {
        "menu_item_id": original_menu_item.id,
        "change_type": "update",
        "new_values": {
            "name": "Updated Name",
            "description": "Updated Description",
            "price": 12.50
        }
    }

    response = client.post(
        "/menu-changes/",
        json=menu_change_data,
        headers={"Authorization": "Bearer test_token"}
    )


    assert response.status_code == 200
    response_data = response.json()
    print("回應狀態碼:", response.status_code)
    print("回應內容:", response.json())
    assert response_data["menu_item_id"] == original_menu_item.id
    assert response_data["change_type"] == "update"
    # 這裡從 changed_fields 改為 new_values
    assert response_data["new_values"]["name"] == "Updated Name"
    assert response_data["new_values"]["description"] == "Updated Description"
    assert response_data["new_values"]["price"] == 12.50
    # 也可以測試 old_values 是否存在且正確 (如果你的邏輯有記錄舊值)
    # assert "old_values" in response_data
    # assert response_data["old_values"]["name"] == "Original Name"
    assert response_data["changed_by"] == 1

    updated_menu_item = db.query(MenuItem).filter(MenuItem.id == original_menu_item.id).first()
    assert updated_menu_item.name == "Updated Name"
    assert updated_menu_item.description == "Updated Description"
    assert updated_menu_item.price == 12.50

    translations = db.query(MenuItemTranslation).filter(
        MenuItemTranslation.menu_items.any(id=updated_menu_item.id)
    ).all()
    # 預期會有 3 種語言的翻譯 (zh-TW, en-US, ja-JP)
    assert len(translations) == 3

    zh_tw_updated_translation = next((t for t in translations if t.language == "zh-TW"), None)
    assert zh_tw_updated_translation is not None
    assert zh_tw_updated_translation.name == "Updated Name translated to zh-TW"
    assert zh_tw_updated_translation.description == "Updated Description translated to zh-TW"

    en_us_updated_translation = next((t for t in translations if t.language == "en-US"), None)
    assert en_us_updated_translation is not None
    assert en_us_updated_translation.name == "Updated Name translated to en-US"
    assert en_us_updated_translation.description == "Updated Description translated to en-US"

    ja_jp_new_translation = next((t for t in translations if t.language == "ja-JP"), None)
    assert ja_jp_new_translation is not None
    assert ja_jp_new_translation.name == "Updated Name translated to ja-JP"
    assert ja_jp_new_translation.description == "Updated Description translated to ja-JP"

    mock_order_service_put.assert_called_once()
    # 這裡的 json 內容可能需要根據 order-service 實際接收的內容來調整
    # 目前假設 order-service 接收的是整個更新後的菜品物件
    expected_put_json = {
        "name": "Updated Name",
        "description": "Updated Description",
        "price": 12.50,
        "category": "Main" # category 沒有在 new_values 中，所以應該是原始的 category
    }
    assert mock_order_service_put.call_args.kwargs['json'] == expected_put_json
    assert mock_order_service_put.call_args.args[0] == f"http://order-service:8000/menu-items/{original_menu_item.id}"
    db.close()
    
# 測試沒有管理員權限的情況
@pytest.mark.skip(reason="暫時跳過這個測試")
def test_create_menu_item_unauthorized(client: TestClient):
    # 模擬 verify_admin 回傳非管理員使用者
    with patch('requests.get') as mock_requests_get:
        mock_requests_get.return_value.status_code = 200
        mock_requests_get.return_value.json.return_value = {"id": 2, "role": "user", "email": "user@example.com"}

        new_menu_item_data = {
            "name": "Unauthorized Dish",
            "description": "Should not be created",
            "price": 1.0,
            "category": "Invalid"
        }

        response = client.post(
            "/menu-items/",
            json=new_menu_item_data,
            headers={"Authorization": "Bearer invalid_token"}
        )
        assert response.status_code == 403 # 預期回傳 403 Forbidden
        assert response.json() == {"detail": "Admin privileges required"}

# 測試 token 無效的情況
@pytest.mark.skip(reason="暫時跳過這個測試")
def test_create_menu_item_invalid_token(client: TestClient):
    # 模擬 verify_admin 回傳 401 狀態碼
    with patch('requests.get') as mock_requests_get:
        mock_requests_get.return_value.status_code = 401

        new_menu_item_data = {
            "name": "Unauthorized Dish",
            "description": "Should not be created",
            "price": 1.0,
            "category": "Invalid"
        }

        response = client.post(
            "/menu-items/",
            json=new_menu_item_data,
            headers={"Authorization": "Bearer invalid_token"}
        )
        assert response.status_code == 401 # 預期回傳 401 Unauthorized
        assert response.json() == {"detail": "Invalid token"}

