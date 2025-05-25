from fastapi import FastAPI, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from typing import List, Dict, Optional
import sys
print(sys.path)
import requests
from datetime import datetime, timedelta
from . import models, schemas, database
from .database import get_db
from googletrans import Translator # 引入 googletrans
import pika
import json

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


from fastapi.security import OAuth2PasswordBearer # 引入 OAuth2PasswordBearer
from .rabbitmq import send_notifications_to_users, send_menu_notification

# 1. 定義資料庫 URL，確保這個 URL 和 docker-compose.yml 裡的一致
SQLALCHEMY_DATABASE_URL = "postgresql://postgres:password@postgres-admin:5432/meal_provider_admin"  

# 2. 建立 SQLAlchemy engine
engine = create_engine(SQLALCHEMY_DATABASE_URL)

# 3. (Optional) 建立 SessionLocal
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 4. 將  models.Base.metadata.create_all(bind=engine)  放在這裡
#models.Base.metadata.create_all(bind=engine) # 加入這一行




app = FastAPI(title="Admin Service API")

# 其他服務的URL（在k8s中會通過服務發現來獲取）
USER_SERVICE_URL = "http://user-service:8000"
ORDER_SERVICE_URL = "http://order-service:8000"

# 新增 OAuth2PasswordBearer 實例
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token") # 這裡的 "token" 是 User Service 的登入端點

# 驗證管理員權限的依賴
# 修改這個函數來調用 User Service
async def verify_admin(token: str, db: Session = Depends(get_db)):
    try:
        response = requests.get(
            f"{USER_SERVICE_URL}/users/me",
            headers={"Authorization": f"Bearer {token}"}
        )
        if response.status_code != 200:
            raise HTTPException(status_code=401, detail="Invalid token")
        
        user_data = response.json()
        if user_data["role"] != "admin":
            raise HTTPException(status_code=403, detail="Admin privileges required")
        return user_data
    except requests.RequestException:
        raise HTTPException(status_code=503, detail="User service unavailable")


# 取得菜品
# 取得所有菜品
@app.get("/menu-items/", response_model=List[Dict])
async def get_all_menu_items(
    language: str = Query("zh-TW", description="Language of the menu item names"),
    db: Session = Depends(get_db),
    admin: dict = Depends(verify_admin)
):
    menu_items = db.query(models.MenuItem).all()
    results = []
    for item in menu_items:
        name = get_menu_item_name_by_language(db, item.id, language)
        description = get_menu_item_description_by_language(db, item.id, language)
        results.append({
            "id": item.id,
            "name": name,
            "description": description,
            "price": item.price,
            "category": item.category
        })
    return results

# 取得菜品 (根據 ID)
@app.get("/menu-items/{menu_item_id}", response_model=Dict)
async def get_menu_item(
    menu_item_id: int,
    language: str = Query("zh-TW", description="Language of the menu item name"),
    db: Session = Depends(get_db),
    admin: dict = Depends(verify_admin)
):
    menu_item = db.query(models.MenuItem).filter(models.MenuItem.id == menu_item_id).first()
    if not menu_item:
        raise HTTPException(status_code=404, detail="Menu item not found")

    name = get_menu_item_name_by_language(db, menu_item_id, language)
    description = get_menu_item_description_by_language(db, menu_item_id, language)

    return {
        "id": menu_item.id,
        "name": name,
        "description": description,
        "price": menu_item.price,
        "category": menu_item.category
    }



# 翻譯文字的函式
def translate_text(text: str, target_language: str) -> str:
    translator = Translator()
    try:
        translation = translator.translate(text, dest=target_language)
        return translation.text
    except Exception as e:
        print(f"Translation failed: {e}") # 記錄錯誤
        return text # 翻譯失敗，回傳原文
# 刪除菜品
@app.delete("/menu-items/{menu_item_id}", response_model=Dict)
async def delete_menu_item(
    menu_item_id: int,
    db: Session = Depends(get_db),
    admin: dict = Depends(verify_admin)
):
    menu_item = db.query(models.MenuItem).filter(models.MenuItem.id == menu_item_id).first()
    if not menu_item:
        raise HTTPException(status_code=404, detail="Menu item not found")

    db.delete(menu_item)
    db.commit()
    return {"message": f"Menu item with id {menu_item_id} deleted successfully"}


# 新增菜單的路由
@app.post("/menu-items/", response_model=schemas.MenuItem)
async def create_menu_item(
    menu_item: schemas.MenuItemCreate,
    db: Session = Depends(get_db),
    admin: dict = Depends(verify_admin)
):
    db_menu_item = models.MenuItem(**menu_item.dict())
    db.add(db_menu_item)
    db.commit()
    db.refresh(db_menu_item)

    # 翻譯菜品名稱和描述
    languages = ["zh-TW", "en-US", "ja-JP"] # 支援的語言
    for lang in languages:
        translated_name = translate_text(menu_item.name, lang)
        translated_description = translate_text(menu_item.description, lang)

        new_translation = models.MenuItemTranslation(
            language=lang,
            name=translated_name,
            description=translated_description
        )
        db_menu_item.translations.append(new_translation)
    db.commit()
    db.refresh(db_menu_item)

    # 通知訂單服務 (簡化，只傳遞新增的菜品 ID)
    try:
        #requests.post(
        #    f"{ORDER_SERVICE_URL}/menu-items/",
        #    json={"menu_item_id": db_menu_item.id}
        #)

        # menu_item to dict
        # send in rabbitmq with serialized schemas.MenuItemCreate
        dictionalized_menu_item = {
            "ZH_name": menu_item.ZH_name,
            "EN_name": menu_item.EN_name,
            "price": menu_item.price,
            "URL": menu_item.URL,
            "is_available": menu_item.is_available
        }
        send_menu_notification(dictionalized_menu_item)
    except requests.RequestException:
        pass # 處理連線錯誤

    return db_menu_item

# 菜單變更相關路由
@app.post("/menu-changes/", response_model=schemas.MenuChange)
async def create_menu_change(
    menu_change: schemas.MenuChangeCreate,
    db: Session = Depends(get_db),
    admin: dict = Depends(verify_admin)
):
    # 1. 取得要修改的菜品
    menu_item = db.query(models.MenuItem).filter(models.MenuItem.id == menu_change.menu_item_id).first()
    if not menu_item:
        raise HTTPException(status_code=404, detail="Menu item not found")

    # 記錄實際被修改的欄位及其新值 (這將成為 models.MenuChange 的 new_values)
    new_values_for_db = {}
    # 記錄被修改欄位的舊值 (這將成為 models.MenuChange 的 old_values)
    old_values_for_db = {}

    # 2. 記錄修改的欄位和新值
    # 這裡的邏輯需要確保只有實際變化的值才被記錄
    if menu_change.new_values.get("name") is not None and menu_item.name != menu_change.new_values["name"]:
        old_values_for_db["name"] = menu_item.name
        new_values_for_db["name"] = menu_change.new_values["name"]
        menu_item.name = menu_change.new_values["name"]
    
    if menu_change.new_values.get("description") is not None and menu_item.description != menu_change.new_values["description"]:
        old_values_for_db["description"] = menu_item.description
        new_values_for_db["description"] = menu_change.new_values["description"]
        menu_item.description = menu_change.new_values["description"]
    
    if menu_change.new_values.get("price") is not None and menu_item.price != menu_change.new_values["price"]:
        old_values_for_db["price"] = menu_item.price
        new_values_for_db["price"] = menu_change.new_values["price"]
        menu_item.price = menu_change.new_values["price"]
    
    if menu_change.new_values.get("category") is not None and menu_item.category != menu_change.new_values["category"]:
        old_values_for_db["category"] = menu_item.category
        new_values_for_db["category"] = menu_change.new_values["category"]
        menu_item.category = menu_change.new_values["category"]

    # 如果沒有任何欄位被修改，拋出錯誤或回傳特定訊息
    if not new_values_for_db:
        raise HTTPException(status_code=400, detail="No changes detected for menu item.")
    
    # === 關鍵修改：在這裡提交 menu_item 的變更 ===
    # 因為 menu_item 已經是從 session 中查詢出來的，所以通常不需要 db.add(menu_item)
    # 但 db.commit() 和 db.refresh(menu_item) 是必須的。
    db.commit() # 將對 menu_item 的修改寫入資料庫
    db.refresh(menu_item) # 刷新 menu_item 物件，確保其屬性反映資料庫的最新狀態

    # 3. 翻譯菜品名稱和描述
    # 僅在 name 或 description 實際改變時才進行翻譯
    if "name" in new_values_for_db or "description" in new_values_for_db:
        languages = ["zh-TW", "en-US", "ja-JP"] # 支援的語言
        for lang in languages:
            # 確保傳遞給 translate_text 的是最新值 (此時 menu_item 已經被刷新)
            translated_name = translate_text(menu_item.name, lang)
            translated_description = translate_text(menu_item.description, lang)

            # 4. 檢查是否已存在該語言的翻譯
            translation = next((t for t in menu_item.translations if t.language == lang), None)

            if translation:
                translation.name = translated_name
                translation.description = translated_description
            else:
                # 5. 如果不存在，則新增
                new_translation = models.MenuItemTranslation(
                    language=lang,
                    name=translated_name,
                    description=translated_description
                )
                menu_item.translations.append(new_translation)
        
        # 如果翻譯有變更，也需要提交翻譯的變更
        db.commit() # 提交翻譯的變更
        db.refresh(menu_item) # 刷新 menu_item 以確保其 translations 關聯是最新狀態


    # 6. 建立 MenuChange 紀錄
    db_menu_change = models.MenuChange(
        menu_item_id=menu_item.id,
        change_type=menu_change.change_type,
        old_values=old_values_for_db, # 填充 old_values
        new_values=new_values_for_db, # 填充 new_values
        changed_by=admin["id"]
    )
    db.add(db_menu_change)
    db.commit()
    db.refresh(db_menu_change)
    
    # 7. 通知訂單服務
    try:
        order_service_url = f"http://order-service:8000/menu-items/{menu_item.id}"
        updated_menu_item_data = {
            "name": menu_item.name,
            "description": menu_item.description,
            "price": menu_item.price,
            "category": menu_item.category,
        }
        # response = requests.put(order_service_url, json=updated_menu_item_data)
        # response.raise_for_status()
        # ==== Try to change to MQ ====
        send_menu_notification()
    except requests.exceptions.RequestException as e:
        print(f"Failed to notify Order Service about menu change: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to notify Order Service: {e}")

    return db_menu_change


# 取得特定語言的菜品名稱
def get_menu_item_name_by_language(db: Session, menu_item_id: int, language: str) -> str:
    menu_item = db.query(models.MenuItem).filter(models.MenuItem.id == menu_item_id).first()
    if not menu_item:
        return ""

    translation = db.query(models.MenuItemTranslation).filter(
        models.MenuItemTranslation.menu_items.any(id=menu_item.id),
        models.MenuItemTranslation.language == language
    ).first()

    if translation:
        return translation.name
    return menu_item.name # 如果找不到指定語言的翻譯，回傳預設名稱

# 取得特定語言的菜品描述
def get_menu_item_description_by_language(db: Session, menu_item_id: int, language: str) -> str:
    menu_item = db.query(models.MenuItem).filter(models.MenuItem.id == menu_item_id).first()
    if not menu_item:
        return ""

    translation = db.query(models.MenuItemTranslation).filter(
        models.MenuItemTranslation.menu_items.any(id=menu_item.id),
        models.MenuItemTranslation.language == language
    ).first()

    if translation:
        return translation.description
    return menu_item.description # 如果找不到指定語言的翻譯，回傳預設名稱


# 賬單通知相關路由
@app.post("/billing-notifications/", response_model=List[schemas.BillingNotification])
async def create_billing_notifications(
    db: Session = Depends(get_db),
    admin: dict = Depends(verify_admin)
):
    # 獲取所有未結賬的訂單
    try:
        response = requests.get(f"{ORDER_SERVICE_URL}/orders/unpaid")
        unpaid_orders = response.json()
    except requests.RequestException:
        raise HTTPException(status_code=503, detail="Order service unavailable")

    # 按用戶分組並創建賬單通知
    notifications = []
    user_orders = {}
    for order in unpaid_orders:
        if order["user_id"] not in user_orders:
            user_orders[order["user_id"]] = []
        user_orders[order["user_id"]].append(order)

    for user_id, orders in user_orders.items():
        total_amount = sum(order["total_amount"] for order in orders)
        notification = models.BillingNotification(
            user_id=user_id,
            total_amount=total_amount,
            billing_period_start=datetime.utcnow() - timedelta(days=30),
            billing_period_end=datetime.utcnow(),
            status="sent"
        )
        db.add(notification)
        notifications.append(notification)

    db.commit()
    return notifications

# 分析報表相關路由
@app.post("/analytics/", response_model=schemas.Analytics)
async def generate_analytics(
    report_type: str,
    report_period: str,
    db: Session = Depends(get_db),
    admin: dict = Depends(verify_admin)
):
    try:
        # 從訂單服務獲取數據
        response = requests.get(
            f"{ORDER_SERVICE_URL}/orders/analytics",
            params={"report_type": report_type, "period": report_period}
        )
        order_data = response.json()

        # 創建分析報表
        analytics = models.Analytics(
            report_type=report_type,
            report_period=report_period,
            report_date=datetime.utcnow(),
            data=order_data
        )
        db.add(analytics)
        db.commit()
        db.refresh(analytics)
        return analytics
    except requests.RequestException:
        raise HTTPException(status_code=503, detail="Order service unavailable")

@app.get("/analytics/", response_model=List[schemas.Analytics])
async def get_analytics(
    report_type: Optional[str] = None,
    db: Session = Depends(get_db),
    admin: dict = Depends(verify_admin)
):
    query = db.query(models.Analytics)
    if report_type:
        query = query.filter(models.Analytics.report_type == report_type)
    return query.all()

# Get all dining records
@app.get("/dining-records/", response_model=List[Dict])
async def get_all_dining_records(
    db: Session = Depends(get_db),
    admin: dict = Depends(verify_admin)
):
    try:
        # Forward request to user service with API key
        response = requests.get(
            f"{USER_SERVICE_URL}/dining-records/",
            headers={
                "Authorization": f"Bearer {admin['token']}",
                "X-API-Key": "mealprovider_admin_key"
            }
        )
        if response.status_code != 200:
            raise HTTPException(
                status_code=response.status_code,
                detail="Failed to fetch dining records from user service"
            )
        return response.json()
    except requests.RequestException:
        raise HTTPException(
            status_code=503,
            detail="User service unavailable"
        )

# Get all unpaid users
@app.get("/users/unpaid", response_model=List[Dict])
async def get_unpaid_users(
    db: Session = Depends(get_db),
    admin: dict = Depends(verify_admin)
):
    try:
        # Forward request to user service with API key
        response = requests.get(
            f"{USER_SERVICE_URL}/users/unpaid",
            headers={
                "Authorization": f"Bearer {admin['token']}",
                "X-API-Key": "mealprovider_admin_key"
            }
        )
        if response.status_code != 200:
            raise HTTPException(
                status_code=response.status_code,
                detail="Failed to fetch unpaid users from user service"
            )
        return response.json()
    except requests.RequestException:
        raise HTTPException(
            status_code=503,
            detail="User service unavailable"
        )

# Send billing notifications
@app.post("/billing-notifications/send", response_model=Dict)
async def send_billing_notifications(
    db: Session = Depends(get_db),
    admin: dict = Depends(verify_admin)
):
    try:
        # Get unpaid users from user service
        response = requests.get(
            f"{USER_SERVICE_URL}/users/unpaid",
            headers={
                "Authorization": f"Bearer {admin['token']}",
                "X-API-Key": "mealprovider_admin_key"
            }
        )
        if response.status_code != 200:
            raise HTTPException(
                status_code=response.status_code,
                detail="Failed to fetch unpaid users from user service"
            )
        
        unpaid_users = response.json()
        
        # Send notifications using the RabbitMQ module
        notified_count = send_notifications_to_users(unpaid_users)
        
        return {
            "message": f"Billing notifications sent to {notified_count} users",
            "notified_users": notified_count
        }
        
    except requests.RequestException:
        raise HTTPException(
            status_code=503,
            detail="User service unavailable"
        )
    except pika.exceptions.AMQPConnectionError:
        raise HTTPException(
            status_code=503,
            detail="Message broker unavailable"
        )