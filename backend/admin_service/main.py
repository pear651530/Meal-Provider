# main.py
from fastapi import FastAPI, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from typing import List, Dict, Optional
import requests
from datetime import datetime, timedelta
import models
import schemas
from database import get_db, Base, engine # <-- 確保從 database.py 導入 Base 和 engine
from fastapi.responses import StreamingResponse
import io
import csv
import pika
import json
from rabbitmq import send_notifications_to_users, send_menu_notification
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi import HTTPException, status
from fastapi import Security
from googletrans import Translator
from fastapi.middleware.cors import CORSMiddleware
import jwt
from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST
from starlette.responses import Response

app = FastAPI(title="Admin Service API")
origins = [
    "http://localhost:5173",  # 你的前端網址
    "http://127.0.0.1:5173",
    "http://localhost:8080",
    "http://127.0.0.1:8080",
    "http://meal-provider.example.com",  
    "https://meal-provider.example.com"  
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,           # 允許的來源清單
    allow_credentials=True,          # 允許跨域時帶 Cookie
    allow_methods=["*"],             # 允許所有 HTTP 方法 (GET, POST, etc)
    allow_headers=["*"],             # 允許所有標頭
    expose_headers=["*"]
)
USER_SERVICE_URL = "http://user-service:8000"
ORDER_SERVICE_URL = "http://order-service:8000"

from fastapi import Request 
from fastapi.responses import JSONResponse
security = HTTPBearer(auto_error=False)
# JWT configuration
SECRET_KEY = "mealprovider"  # Should be obtained from environment variables in production
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
async def verify_admin(
    request: Request,
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    # 針對 OPTIONS 請求，直接返回，不進行 JWT 驗證
    # CORSMiddleware 會處理其 CORS 標頭
    if request.method == "OPTIONS":
        return JSONResponse(content={"message": "CORS preflight handled by verify_admin"}, status_code=200)

    # 只有在非 OPTIONS 請求時，才進行憑證檢查
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing authorization header"
        )
    
    token = credentials.credentials
    
    try:
        # Decode and verify the JWT token directly
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        print(f"Decoded payload: {payload}") 
        # Check if token is expired
        exp = payload.get("exp")
        if exp is None or datetime.utcnow().timestamp() > exp:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token has expired"
            )
        
        # Get role from token payload
        role = payload.get("role")
        print(f"Decoded role: {role}")  # Debugging line to check role
        if role != "admin" and role != "super_admin":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Admin privileges required"
            )    
        payload["token"] = token
        return payload
        
    except jwt.PyJWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )
translator = Translator()

async def validate_and_translate_names(zh_name: str, en_name: str) -> tuple[str, str]:
    """
    檢查 zh_name 與 en_name 是否同時為空，若其中一方為空白，則用翻譯補上。

    :param zh_name: 中文名稱（可空白）
    :param en_name: 英文名稱（可空白）
    :return: 傳回補齊後的 (zh_name, en_name)
    :raises HTTPException: 兩者同時空白時拋錯
    """
    zh = zh_name.strip() if isinstance(zh_name, str) else ""
    en = en_name.strip() if isinstance(en_name, str) else ""

    if zh == "" and en == "":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="At least one of zh_name or en_name must be provided."
        )

    if zh == "":
        result = await translator.translate(en, dest='zh-TW')
        zh = result.text

    if en == "":
        result = await translator.translate(zh, dest='en')
        en = result.text

    return zh, en
@app.get("/test/")
async def test_endpoint():
    return {"message": "Test successful!"}

# 取得所有菜品
@app.get("/menu-items/", response_model=List[schemas.MenuItem])
async def get_all_menu_items(
    db: Session = Depends(get_db),
   # admin: dict = Security(verify_admin)
) -> List[schemas.MenuItem]:
    # 軟刪除後，預設只顯示未被軟刪除的菜品
    menu_items = db.query(models.MenuItem).filter(models.MenuItem.is_deleted == False).all()
    return [schemas.MenuItem.from_orm(item) for item in menu_items]

# 取得單一菜品 (根據 ID)
@app.get("/menu-items/{menu_item_id}", response_model=schemas.MenuItem)
async def get_menu_item(
    menu_item_id: int,
    db: Session = Depends(get_db),
    #admin: dict = Security(verify_admin)
) -> schemas.MenuItem:
    # 軟刪除後，預設只查詢未被軟刪除的菜品
    menu_item = db.query(models.MenuItem).filter(
        models.MenuItem.id == menu_item_id, 
        #models.MenuItem.is_deleted == False
    ).first()
    if not menu_item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Menu item not found or has been deleted")
    return schemas.MenuItem.from_orm(menu_item)

## 新增軟刪除的路由 (取代原硬刪除)
@app.delete("/menu-items/{menu_item_id}", status_code=status.HTTP_200_OK) # 將硬刪除路由改為軟刪除，移除 /hard-delete
async def soft_delete_menu_item( # 函數名稱也改為 soft_delete
    menu_item_id: int,
    db: Session = Depends(get_db),      
    admin: dict = Security(verify_admin)
) -> Dict[str, str]:
    menu_item = db.query(models.MenuItem).filter(
        models.MenuItem.id == menu_item_id,
        models.MenuItem.is_deleted == False # 確保要刪除的菜品尚未被軟刪除
    ).first()
    if not menu_item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Menu item not found or already deleted")

    # 記錄舊值（軟刪除前）
    old_values_for_db = {
        "zh_name": menu_item.zh_name,
        "en_name": menu_item.en_name,
        "price": menu_item.price,
        "url": menu_item.url,
        "is_available": menu_item.is_available,
        "is_deleted": menu_item.is_deleted, # 記錄舊的 is_deleted 狀態
        "deleted_at": str(menu_item.deleted_at) if menu_item.deleted_at else None # 記錄舊的 deleted_at
    }

    admin_role_to_id_map = {
        "admin": 1,
        "super_admin": 2,
    }
    user_role_from_jwt = admin.get("role")
    changed_by_id = admin_role_to_id_map.get(user_role_from_jwt, 0)

    # 執行軟刪除：更新 is_deleted 標誌和 deleted_at 時間
    menu_item.is_deleted = True
    menu_item.deleted_at = datetime.utcnow() # 設定刪除時間
    
    db.commit() # 提交 MenuItem 的更新
    db.refresh(menu_item) # 刷新以獲取更新後的狀態

    # 記錄變更：change_type 為 "soft_remove"
    db_menu_change = models.MenuChange(
        menu_item_id=menu_item.id,
        change_type="soft_remove", # 變更類型改為 "soft_remove"
        old_values=old_values_for_db,
        new_values={ # 記錄新的狀態
            "is_deleted": menu_item.is_deleted,
            "deleted_at": str(menu_item.deleted_at) # 記錄新的 deleted_at
        },
        changed_by=changed_by_id
    )
    db.add(db_menu_change)
    db.commit()
    db.refresh(db_menu_change)
    return {"message": f"Menu item with id {menu_item_id} soft deleted successfully and change recorded."}

# 上架/下架菜單項目 (無需大改動，但要注意查詢時預設不包含已刪除的)
@app.put("/menu-items/{menu_item_id}/toggle-availability", response_model=schemas.MenuItem)
async def toggle_menu_item_availability(
    menu_item_id: int,
    db: Session = Depends(get_db),
    admin: dict = Security(verify_admin)
) -> schemas.MenuItem:
    """
    切換菜單項目的上架/下架狀態 (is_available)。
    """
    # 查詢時加上 is_deleted == False
    menu_item = db.query(models.MenuItem).filter(
        models.MenuItem.id == menu_item_id,
        models.MenuItem.is_deleted == False # 確保只能操作未刪除的菜品
    ).first()
    if not menu_item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Menu item not found or has been deleted")

    old_is_available = menu_item.is_available
    new_is_available = not old_is_available # 切換狀態

    old_values_for_db = {"is_available": old_is_available}
    new_values_for_db = {"is_available": new_is_available}

    menu_item.is_available = new_is_available # 更新 ORM 對象的狀態
    db.commit()
    db.refresh(menu_item)
    
    admin_role_to_id_map = {
        "admin": 1,
        "super_admin": 2,
    }
    user_role_from_jwt = admin.get("role")
    changed_by_id = admin_role_to_id_map.get(user_role_from_jwt, 0)

    # 記錄變更
    db_menu_change = models.MenuChange(
        menu_item_id=menu_item_id,
        change_type="toggle_availability",
        old_values=old_values_for_db,
        new_values=new_values_for_db,
        changed_by=changed_by_id
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
    admin: dict = Security(verify_admin) #至關掉FOR TEST
) -> schemas.MenuItem:
    """
    新增一個新的菜單項目，並記錄變更。
    """
    zh, en =await validate_and_translate_names(menu_item.zh_name, menu_item.en_name)
    menu_item.zh_name = zh
    menu_item.en_name = en
    # 將 Pydantic 模型轉換為 SQLAlchemy 模型
    db_menu_item = models.MenuItem(**menu_item.dict())
    db.add(db_menu_item)
    db.commit()
    db.refresh(db_menu_item) # 刷新以獲取由資料庫生成的 ID 和時間戳
    admin_role_to_id_map = {
        "admin": 1,        # 為 'admin' 角色指定一個整數 ID
        "super_admin": 2,  # 為 'super_admin' 角色指定一個整數 ID
        # 如果未來有其他管理員角色，可以在這裡添加更多映射
    }
    user_role_from_jwt = admin.get("role")
    changed_by_id = admin_role_to_id_map.get(user_role_from_jwt, 0) 
    # new_values 就是新增的菜單項目內容
    new_values_for_db = menu_item.dict()
    db_menu_change = models.MenuChange(
        menu_item_id=db_menu_item.id,
        change_type="add",
        old_values=None, # 新增時沒有舊值
        new_values=new_values_for_db,
        changed_by=changed_by_id
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
            "zh_name": menu_item.zh_name,
            "en_name": menu_item.en_name,
            "price": menu_item.price,
            "url": menu_item.url,
            "is_available": menu_item.is_available
        }
        send_menu_notification(dictionalized_menu_item)
    except requests.RequestException:
        pass # 處理連線錯誤

    return schemas.MenuItem.from_orm(db_menu_item)




# 菜單變更相關路由 (更新菜單項目並記錄變更)
@app.put("/menu-items/{menu_item_id}/", response_model=schemas.MenuChange)
async def update_menu_item_and_record_change(
    menu_item_id: int,
    menu_change_data: schemas.MenuChangeCreate,
    db: Session = Depends(get_db),
    admin: dict = Security(verify_admin)
) -> schemas.MenuChange:
    """
    更新菜單項目並記錄其變更。
    """
    if menu_item_id != menu_change_data.menu_item_id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Menu item ID in path and request body do not match.")

    # 查詢時加上 is_deleted == False
    menu_item = db.query(models.MenuItem).filter(
        models.MenuItem.id == menu_item_id,
        models.MenuItem.is_deleted == False # 確保只能更新未刪除的菜品
    ).first()
    if not menu_item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Menu item not found or has been deleted")
    
    new_ZH = menu_change_data.new_values.get("zh_name", menu_item.zh_name)
    new_EN = menu_change_data.new_values.get("en_name", menu_item.en_name)
    zh, en = await validate_and_translate_names(new_ZH, new_EN)
    menu_change_data.new_values["zh_name"] = zh
    menu_change_data.new_values["en_name"] = en
    
    new_values_for_db = {}
    old_values_for_db = {}

    update_fields = ["zh_name", "en_name", "price", "url", "is_available"]
    
    for field in update_fields:
        if field in menu_change_data.new_values and getattr(menu_item, field) != menu_change_data.new_values[field]:
            old_values_for_db[field] = getattr(menu_item, field)
            setattr(menu_item, field, menu_change_data.new_values[field])
            new_values_for_db[field] = menu_change_data.new_values[field]

    if not new_values_for_db:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No changes detected for menu item.")
    
    db.commit()
    db.refresh(menu_item)

    admin_role_to_id_map = {
        "admin": 1,
        "super_admin": 2,
    }
    user_role_from_jwt = admin.get("role")
    changed_by_id = admin_role_to_id_map.get(user_role_from_jwt, 0)

    db_menu_change = models.MenuChange(
        menu_item_id=menu_item.id,
        change_type=menu_change_data.change_type,
        old_values=old_values_for_db,
        new_values=new_values_for_db,
        changed_by=changed_by_id
    )
    db.add(db_menu_change)
    db.commit()
    db.refresh(db_menu_change)
    
    # 待改:待確認MQ的send_menu_notification要送什麼格式    
    # 7. 通知訂單服務
    #try:
    #   order_service_URL = f"http://order-service:8000/menu-items/{menu_item.id}"
    #    updated_menu_item_data = {
    #        "name": menu_item.name,
    #        "description": menu_item.description,
    #        "price": menu_item.price,
    #        "category": menu_item.category,
    #    }
        # response = requests.put(order_service_URL, json=updated_menu_item_data)
        # response.raise_for_status()
        # ==== Try to change to MQ ====
    #    send_menu_notification()
    #except requests.exceptions.RequestException as e:
    #    print(f"Failed to notify Order Service about menu change: {e}")
    #    raise HTTPException(status_code=500, detail=f"Failed to notify Order Service: {e}")

    try:    
        dictionalized_menu_item = {
            "id": menu_item.id,
            "zh_name": menu_item.zh_name,
            "en_name": menu_item.en_name,
            "price": menu_item.price,
            "url": menu_item.url,
            "is_available": menu_item.is_available,
            "is_deleted": menu_item.is_deleted # 傳遞 is_deleted 狀態
        }
        send_menu_notification(dictionalized_menu_item)
    except Exception as e:
        print(f"Failed to send menu notification: {e}")

    return schemas.MenuChange.from_orm(db_menu_change)

@app.get("/report/analytics", response_class=StreamingResponse)
async def fetch_analytics_report(
    admin: dict = Security(verify_admin),
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
    admin: dict = Security(verify_admin) #至關掉FOR TEST
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
    admin: dict = Security(verify_admin) #至關掉FOR TEST
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
    admin: dict = Security(verify_admin)
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

@app.get("/health")
def health_check():
    return {"status": "ok"}

# Prometheus metrics
REQUEST_COUNT = Counter(
    'admin_service_request_count',
    'Total count of requests',
    ['method', 'endpoint', 'status']
)

REQUEST_LATENCY = Histogram(
    'admin_service_request_latency_seconds',
    'Request latency in seconds',
    ['method', 'endpoint']
)

# Add metrics endpoint
@app.get("/metrics")
async def metrics():
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)

# Add middleware for metrics
@app.middleware("http")
async def metrics_middleware(request, call_next):
    start_time = datetime.utcnow()
    response = await call_next(request)
    duration = (datetime.utcnow() - start_time).total_seconds()
    
    REQUEST_COUNT.labels(
        method=request.method,
        endpoint=request.url.path,
        status=response.status_code
    ).inc()
    
    REQUEST_LATENCY.labels(
        method=request.method,
        endpoint=request.url.path
    ).observe(duration)
    
    return response