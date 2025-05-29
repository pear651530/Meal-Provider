# main.py
from fastapi import FastAPI, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from typing import List, Dict, Optional
import requests
from datetime import datetime, timedelta
from . import models, schemas
from .database import get_db, Base, engine # <-- 確保從 database.py 導入 Base 和 engine
from fastapi.responses import StreamingResponse
import io
import csv
import pika
import json
from .rabbitmq import send_notifications_to_users, send_menu_notification
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi import HTTPException, status
from googletrans import Translator
USER_SERVICE_URL = "http://user-service:8000"
ORDER_SERVICE_URL = "http://order-service:8000"

app = FastAPI(title="Admin Service API")


security = HTTPBearer()

async def verify_admin(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    token = credentials.credentials  # 從 Authorization: Bearer <token> 拿到 token 字串

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



translator = Translator()

async def validate_and_translate_names(ZH_name: str, EN_name: str) -> tuple[str, str]:
    """
    檢查 ZH_name 與 EN_name 是否同時為空，若其中一方為空白，則用翻譯補上。

    :param ZH_name: 中文名稱（可空白）
    :param EN_name: 英文名稱（可空白）
    :return: 傳回補齊後的 (ZH_name, EN_name)
    :raises HTTPException: 兩者同時空白時拋錯
    """
    zh = ZH_name.strip() if isinstance(ZH_name, str) else ""
    en = EN_name.strip() if isinstance(EN_name, str) else ""

    if zh == "" and en == "":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="At least one of ZH_name or EN_name must be provided."
        )

    if zh == "":
        result = await translator.translate(en, dest='zh-TW')
        zh = result.text

    if en == "":
        result = await translator.translate(zh, dest='en')
        en = result.text

    return zh, en

# 取得所有菜品
@app.get("/menu-items/", response_model=List[schemas.MenuItem])
async def get_all_menu_items(
    db: Session = Depends(get_db),
    admin: dict = Depends(verify_admin) 
) -> List[schemas.MenuItem]:
    menu_items = db.query(models.MenuItem).all()
    # 使用 from_orm 方法將 SQLAlchemy ORM 物件轉換為 Pydantic Schema 物件
    return [schemas.MenuItem.from_orm(item) for item in menu_items]


# 取得單一菜品 (根據 ID)
@app.get("/menu-items/{menu_item_id}", response_model=schemas.MenuItem)
async def get_menu_item(
    menu_item_id: int,
    db: Session = Depends(get_db),
    admin: dict = Depends(verify_admin) #至關掉FOR TEST
) -> schemas.MenuItem:
    menu_item = db.query(models.MenuItem).filter(models.MenuItem.id == menu_item_id).first()
    if not menu_item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Menu item not found")
    return schemas.MenuItem.from_orm(menu_item)

# 硬刪除菜品 (將其從資料庫完全移除)
@app.delete("/menu-items/{menu_item_id}/hard-delete", status_code=status.HTTP_200_OK)
async def hard_delete_menu_item(
    menu_item_id: int,
    db: Session = Depends(get_db),
    admin: dict = Depends(verify_admin)
) -> Dict[str, str]:
    menu_item = db.query(models.MenuItem).filter(models.MenuItem.id == menu_item_id).first()
    if not menu_item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Menu item not found")

    # 記錄刪除前的狀態作為 old_values
    old_values_for_db = {
        "ZH_name": menu_item.ZH_name,
        "EN_name": menu_item.EN_name,
        "price": menu_item.price,
        "URL": menu_item.URL,
        "is_available": menu_item.is_available
    }

    db.delete(menu_item)
    db.commit()

    # 創建 MenuChange 記錄
    db_menu_change = models.MenuChange(
        menu_item_id=menu_item_id,
        change_type="hard_remove", # 變更類型改為 'hard_remove' 以示區別
        old_values=old_values_for_db,
        new_values={}, # 刪除時新值為空
        changed_by=admin["id"]
    )
    db.add(db_menu_change)
    db.commit()
    db.refresh(db_menu_change)

    return {"message": f"Menu item with id {menu_item_id} hard deleted successfully and change recorded."}

# 上架/下架菜單項目
@app.put("/menu-items/{menu_item_id}/toggle-availability", response_model=schemas.MenuItem)
async def toggle_menu_item_availability(
    menu_item_id: int,
    db: Session = Depends(get_db),
    admin: dict = Depends(verify_admin) #至關掉FOR TEST
) -> schemas.MenuItem:
    """
    切換菜單項目的上架/下架狀態 (is_available)。
    """
    menu_item = db.query(models.MenuItem).filter(models.MenuItem.id == menu_item_id).first()
    if not menu_item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Menu item not found")

    old_is_available = menu_item.is_available
    new_is_available = not old_is_available # 切換狀態

    old_values_for_db = {"is_available": old_is_available}
    new_values_for_db = {"is_available": new_is_available}

    menu_item.is_available = new_is_available # 更新 ORM 對象的狀態
    db.commit()
    db.refresh(menu_item)

    # 記錄變更
    db_menu_change = models.MenuChange(
        menu_item_id=menu_item_id,
        change_type="toggle_availability",
        old_values=old_values_for_db,
        new_values=new_values_for_db,
        changed_by=admin["id"]
    )
    db.add(db_menu_change)
    db.commit()
    db.refresh(db_menu_change)
    return schemas.MenuItem.from_orm(menu_item)

# 新增菜單項目
@app.post("/menu-items/", response_model=schemas.MenuItem, status_code=status.HTTP_201_CREATED)
async def create_menu_item(
    menu_item: schemas.MenuItemCreate,
    db: Session = Depends(get_db),
    admin: dict = Depends(verify_admin) #至關掉FOR TEST
) -> schemas.MenuItem:
    """
    新增一個新的菜單項目，並記錄變更。
    """
    zh, en =await validate_and_translate_names(menu_item.ZH_name, menu_item.EN_name)
    menu_item.ZH_name = zh
    menu_item.EN_name = en
    # 將 Pydantic 模型轉換為 SQLAlchemy 模型
    db_menu_item = models.MenuItem(**menu_item.dict())
    db.add(db_menu_item)
    db.commit()
    db.refresh(db_menu_item) # 刷新以獲取由資料庫生成的 ID 和時間戳

    # 創建 MenuChange 記錄 (新增操作)
    # new_values 就是新增的菜單項目內容
    new_values_for_db = menu_item.dict()
    db_menu_change = models.MenuChange(
        menu_item_id=db_menu_item.id,
        change_type="add",
        old_values=None, # 新增時沒有舊值
        new_values=new_values_for_db,
        changed_by=admin["id"]
    )
    db.add(db_menu_change)
    db.commit()
    db.refresh(db_menu_change)

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

    return schemas.MenuItem.from_orm(db_menu_item)




# 菜單變更相關路由 (更新菜單項目並記錄變更)
@app.put("/menu-items/{menu_item_id}/", response_model=schemas.MenuChange) # 使用 PUT 請求來更新特定資源
async def update_menu_item_and_record_change( # 將函數名稱改為更具描述性
    menu_item_id: int,
    menu_change_data: schemas.MenuChangeCreate,
    db: Session = Depends(get_db),
    admin: dict = Depends(verify_admin) #至關掉FOR TEST
) -> schemas.MenuChange:
    """
    更新菜單項目並記錄其變更。
    """
    # 檢查 menu_change_data 中的 menu_item_id 是否與 Path 參數一致，增加安全性
    if menu_item_id != menu_change_data.menu_item_id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Menu item ID in path and request body do not match.")

    # 1. 取得要修改的菜品
    menu_item = db.query(models.MenuItem).filter(models.MenuItem.id == menu_item_id).first()
    if not menu_item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Menu item not found")
    
    new_ZH = menu_change_data.new_values.get("ZH_name", menu_item.ZH_name)
    new_EN = menu_change_data.new_values.get("EN_name", menu_item.EN_name)
    zh, en = await validate_and_translate_names(new_ZH, new_EN)
    # 更新回 new_values
    menu_change_data.new_values["ZH_name"] = zh
    menu_change_data.new_values["EN_name"] = en
    # 記錄實際被修改的欄位及其新值
    new_values_for_db = {}
    # 記錄被修改欄位的舊值
    old_values_for_db = {}

    # 遍歷所有可能的 MenuItem 欄位，並檢查 new_values 中是否有對應的更新
    update_fields = ["ZH_name", "EN_name", "price", "URL", "is_available"]
    
    for field in update_fields:
        # 檢查 new_values 中是否存在該欄位，並且值與當前資料庫中的值不同
        if field in menu_change_data.new_values and getattr(menu_item, field) != menu_change_data.new_values[field]:
            old_values_for_db[field] = getattr(menu_item, field)
            setattr(menu_item, field, menu_change_data.new_values[field])
            new_values_for_db[field] = menu_change_data.new_values[field]

    # 如果沒有任何欄位被修改，拋出錯誤或回傳特定訊息
    if not new_values_for_db:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No changes detected for menu item.")
    
    # 提交 menu_item 的變更
    db.commit()
    db.refresh(menu_item) # 刷新 menu_item 物件，確保其屬性反映資料庫的最新狀態

    # 建立 MenuChange 紀錄
    db_menu_change = models.MenuChange(
        menu_item_id=menu_item.id,
        change_type=menu_change_data.change_type, # 使用來自 input 的 change_type (例如 "update")
        old_values=old_values_for_db,
        new_values=new_values_for_db,
        changed_by=admin["id"]
    )
    db.add(db_menu_change)
    db.commit()
    db.refresh(db_menu_change)
    
    # 待改:待確認MQ的send_menu_notification要送什麼格式    
    # 7. 通知訂單服務
    #try:
    #   order_service_url = f"http://order-service:8000/menu-items/{menu_item.id}"
    #    updated_menu_item_data = {
    #        "name": menu_item.name,
    #        "description": menu_item.description,
    #        "price": menu_item.price,
    #        "category": menu_item.category,
    #    }
        # response = requests.put(order_service_url, json=updated_menu_item_data)
        # response.raise_for_status()
        # ==== Try to change to MQ ====
    #    send_menu_notification()
    #except requests.exceptions.RequestException as e:
    #    print(f"Failed to notify Order Service about menu change: {e}")
    #    raise HTTPException(status_code=500, detail=f"Failed to notify Order Service: {e}")

    try: 
        # 將菜單項目轉換為字典格式，並發送到 RabbitMQ
        dictionalized_menu_item = {
            "id": menu_item.id,
            "ZH_name": menu_item.ZH_name,
            "EN_name": menu_item.EN_name,
            "price": menu_item.price,
            "URL": menu_item.URL,
            "is_available": menu_item.is_available
        }
        send_menu_notification(dictionalized_menu_item)
    except pika.exceptions.AMQPConnectionError as e:
        print(f"Failed to send menu notification: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to send menu notification: {str(e)}")

    return schemas.MenuChange.from_orm(db_menu_change)


# 賬單通知相關路由
@app.post("/billing-notifications/", response_model=List[schemas.BillingNotification])
async def create_billing_notifications(
    db: Session = Depends(get_db),
    admin: dict = Depends(verify_admin) #至關掉FOR TEST
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

@app.get("/report/analytics", response_class=StreamingResponse)
async def fetch_analytics_report(
    admin: dict = Depends(verify_admin),
    report_period: str = Query("daily", enum=["daily", "weekly", "monthly"]),
    #GET /report/analytics?report_type=order_trends&report_period=weekly
):
    try:
        response = requests.get(
            f"{ORDER_SERVICE_URL}/api/analytics",
           params={"report_type": "order_trends", "period": report_period}
        )
        if response.status_code != 200:
            raise HTTPException(status_code=response.status_code, detail="Failed to fetch analytics report")

        csv_lines = response.iter_lines(decode_unicode=True)
        reader = csv.DictReader(csv_lines)

        enriched_rows = []
        errors = []

        total_income = 0.0
        total_quantity = 0
        sum_total_reviews = 0
        sum_good_reviews = 0

        for row in reader:
            item_id = row.pop("item_id")

            try:
                # rating_res = requests.get(f"{USER_SERVICE_URL}/ratings/{item_id}")
                rating_res = requests.get(f"{USER_SERVICE_URL}/ratingswithorder/{item_id}")
                if rating_res.status_code == 200:
                    rating_data = rating_res.json()
                    params = [
                        ("report_type", "menu_preferences"),
                        ("report_period", report_period)
                    ]
                    params.extend([("order_ids", oid) for oid in rating_data.get("order_ids", [])])
                    response_with_order_ids = requests.get(
                        f"{ORDER_SERVICE_URL}/api/analytics",
                        params = params
                    )
                    if response_with_order_ids.status_code == 200:
                        csv_lines_with_order_ids = response_with_order_ids.iter_lines(decode_unicode=True)
                        reader_with_order_ids = csv.DictReader(csv_lines_with_order_ids)
                        result_with_order_ids = next(reader_with_order_ids, None)
                        total_order_id_count = int(result_with_order_ids["total_order_ids"])
                        valid_order_id_count = int(result_with_order_ids["recent_orders_within_period"])
                        invalid_order_id_count = total_order_id_count - valid_order_id_count
                        row["total_reviews"] = rating_data["total_reviews"] - invalid_order_id_count
                        row["good_reviews"] = rating_data["good_reviews"] - invalid_order_id_count
                        row["good_ratio"] = round((rating_data["good_reviews"] - invalid_order_id_count) / (rating_data["total_reviews"] - invalid_order_id_count), 2) if (rating_data["total_reviews"] - invalid_order_id_count) > 0 else 0.0
                    else:
                        row["total_reviews"] = rating_data["total_reviews"]
                        row["good_reviews"] = rating_data["good_reviews"]
                        row["good_ratio"] = rating_data["good_ratio"]
                        errors.append(f"menu_item_id {item_id} response {rating_res.status_code}")


                    #row["total_reviews"] = rating_data["total_reviews"]
                    #row["good_reviews"] = rating_data["good_reviews"]
                    #row["good_ratio"] = rating_data["good_ratio"]

                    # ✅ 累加總評論數與好評數
                    sum_total_reviews += int(rating_data["total_reviews"]) - invalid_order_id_count
                    sum_good_reviews += int(rating_data["good_reviews"]) - invalid_order_id_count
                else:
                    row["total_reviews"] = ""
                    row["good_reviews"] = ""
                    row["good_ratio"] = ""
                    errors.append(f"menu_item_id {item_id} response {rating_res.status_code}")
            except requests.RequestException as e:
                row["total_reviews"] = ""
                row["good_reviews"] = ""
                row["good_ratio"] = ""
                errors.append(f"menu_item_id {item_id} error: {str(e)}")

            try:
                total_income += float(row["income"])
                total_quantity += int(row["quantity"])
            except ValueError:
                pass

            enriched_rows.append(row)

        # 加總好評比
        total_good_ratio = round(sum_good_reviews / sum_total_reviews, 2) if sum_total_reviews else ""

        output = io.StringIO()
        fieldnames = list(enriched_rows[0].keys())
        writer = csv.DictWriter(output, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(enriched_rows)

        writer.writerow({
            fieldnames[0]: "TOTAL",
            "quantity": total_quantity,
            "income": f"{total_income:.2f}",
            "total_reviews": sum_total_reviews,
            "good_reviews": sum_good_reviews,
            "good_ratio": total_good_ratio
        })

        # ✅ 加入錯誤提示行
        if errors:
            writer.writerow({
                fieldnames[0]: f"ERROR: {len(errors)} menu items failed to fetch ratings."
            })

        output.seek(0)

        return StreamingResponse(
            output,
            media_type="text/csv",
            headers={"Content-Disposition": "attachment; filename=analytics_with_ratings.csv"}
        )

    except requests.RequestException:
        raise HTTPException(status_code=503, detail="Order or Rating service unavailable")

# Get all dining records
@app.get("/dining-records/", response_model=List[Dict])
async def get_all_dining_records(
    db: Session = Depends(get_db),
    admin: dict = Depends(verify_admin) #至關掉FOR TEST
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
    admin: dict = Depends(verify_admin) #至關掉FOR TEST
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
        if not isinstance(unpaid_users, list):
            raise HTTPException(
                status_code=500,
                detail="Invalid response format from user service"
            )
        
        # Send notifications using the RabbitMQ module
        try:
            notified_count = send_notifications_to_users(unpaid_users)
        except ValueError as e:
            raise HTTPException(
                status_code=500,
                detail=str(e)
            )
        
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