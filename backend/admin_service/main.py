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

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


from fastapi.security import OAuth2PasswordBearer # 引入 OAuth2PasswordBearer
# ... (其他 import 保持不變)

# 1. 定義資料庫 URL，確保這個 URL 和 docker-compose.yml 裡的一致
SQLALCHEMY_DATABASE_URL = "postgresql://postgres:password@postgres-admin:5432/meal_provider_admin"  

# 2. 建立 SQLAlchemy engine
engine = create_engine(SQLALCHEMY_DATABASE_URL)

# 3. (Optional) 建立 SessionLocal
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 4. 將  models.Base.metadata.create_all(bind=engine)  放在這裡
models.Base.metadata.create_all(bind=engine) # 加入這一行




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
        requests.post(
            f"{ORDER_SERVICE_URL}/menu-items/",
            json={"menu_item_id": db_menu_item.id}
        )
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

    changed_fields = {}

    # 2. 記錄修改的欄位和新值
    if menu_change.new_values.get("name") is not None and menu_item.name != menu_change.new_values["name"]:
        changed_fields["name"] = menu_change.new_values["name"]
        menu_item.name = menu_change.new_values["name"]
    if menu_change.new_values.get("description") is not None and menu_item.description != menu_change.new_values["description"]:
        changed_fields["description"] = menu_change.new_values["description"]
        menu_item.description = menu_change.new_values["description"]
    if menu_change.new_values.get("price") is not None and menu_item.price != menu_change.new_values["price"]:
        changed_fields["price"] = menu_change.new_values["price"]
        menu_item.price = menu_change.new_values["price"]
    if menu_change.new_values.get("category") is not None and menu_item.category != menu_change.new_values["category"]:
        changed_fields["category"] = menu_change.new_values["category"]
        menu_item.category = menu_change.new_values["category"]

    # 3. 翻譯菜品名稱和描述
    if "name" in changed_fields or "description" in changed_fields:
        languages = ["zh-TW", "en-US", "ja-JP"] # 支援的語言
        for lang in languages:
            translated_name = translate_text(changed_fields.get("name", menu_item.name), lang)
            translated_description = translate_text(changed_fields.get("description", menu_item.description), lang)

            # 4. 檢查是否已存在該語言的翻譯
            translation = db.query(models.MenuItemTranslation).filter(
                models.MenuItemTranslation.menu_items.any(id=menu_item.id),
                models.MenuItemTranslation.language == lang
            ).first()

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

    # 6. 建立 MenuChange 紀錄
    db_menu_change = models.MenuChange(
        menu_item_id=menu_item.id,
        change_type=menu_change.change_type,
        changed_fields=changed_fields,
        changed_by=admin["id"]
    )
    db.add(db_menu_change)
    db.commit()
    db.refresh(db_menu_change)

    # 7. 更新訂單服務 (簡化，只傳 menu_item_id)
    try:
        requests.put(
            f"{ORDER_SERVICE_URL}/menu-items/{menu_change.menu_item_id}",
            json={"menu_item_id": menu_change.menu_item_id} 
        )
    except requests.RequestException:
        pass

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
