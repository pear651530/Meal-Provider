
import requests
import io
import os
if os.getenv("IS_TEST") != "true":
    from .init_db import init_db
    init_db()
from fastapi import FastAPI, Depends, HTTPException, APIRouter, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime
from sqlalchemy import func
from datetime import date, datetime, time ,timedelta

from . import models, schemas, database
from .database import get_db
from .rabbitmq import *

app = FastAPI(title="Order Service API")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 用戶服務URL（在k8s中會通過服務發現來獲取）
USER_SERVICE_URL = "http://user-service:8000"

consumer_thread = None

@app.on_event("startup")
async def startup_event():
    from .database import engine
    from .models import Base

    def init_db():
        Base.metadata.create_all(bind=engine)

    print("Creating database tables...")
    init_db()
    print("Database tables created successfully!")
    """Initialize services on startup"""
    
    # Get a database session
    db = next(get_db())
    
    try:
        if os.getenv("IS_TEST") != "true":
            global consumer_thread
            # Set up RabbitMQ
            setup_rabbitmq()
            # Start the consumer thread
            consumer_thread = start_consumer_thread(db)
    finally:
        db.close()

@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    global consumer_thread
    if consumer_thread and consumer_thread.is_alive():
        # The thread is a daemon thread, so it will be terminated when the main process exits
        pass


# 驗證用戶token的依賴
async def verify_token(token: str, db: Session = Depends(get_db)):
    try:
        response = requests.get(
            f"{USER_SERVICE_URL}/users/me",
            headers={"Authorization": f"Bearer {token}"}
        )
        if response.status_code == 200:
            return response.json()
        raise HTTPException(status_code=401, detail="Invalid token")
    except requests.RequestException:
        raise HTTPException(status_code=503, detail="User service unavailable")

# 菜單項目相關路由
@app.post("/menu-items/", response_model=schemas.MenuItem)
def create_menu_item(
    menu_item: schemas.MenuItemCreate,
    db: Session = Depends(get_db)
):
    db_menu_item = models.MenuItem(**menu_item.dict())
    db.add(db_menu_item)
    db.commit()
    db.refresh(db_menu_item)
    return db_menu_item

@app.get("/menu-items/", response_model=List[schemas.MenuItem])
def get_menu_items(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    return db.query(models.MenuItem).offset(skip).limit(limit).all()

# 訂單相關路由
@app.post("/orders/", response_model=schemas.Order)
async def create_order(
    order: schemas.OrderCreate,
    db: Session = Depends(get_db)
):
    # 計算訂單總金額
    total_amount = 0
    for item in order.items:
        menu_item = db.query(models.MenuItem).filter(models.MenuItem.id == item.menu_item_id).first()
        if not menu_item:
            raise HTTPException(status_code=404, detail=f"Menu item {item.menu_item_id} not found")
        if not menu_item.is_available:
            pass
            #raise HTTPException(status_code=400, detail=f"Menu item {menu_item.en_name} is not available")
        total_amount += menu_item.price * item.quantity

    # 創建訂單
    db_order = models.Order(
        user_id=order.user_id,
        total_amount=total_amount,
        payment_method=order.payment_method,
        payment_status=order.payment_status,
    )
    db.add(db_order)
    db.commit()
    db.refresh(db_order)

    # 添加訂單項目
    for item in order.items:
        db_order_item = models.OrderItem(
            order_id=db_order.id,
            menu_item_id=item.menu_item_id,
            quantity=item.quantity,
            unit_price=db.query(models.MenuItem).get(item.menu_item_id).price
        )
        db.add(db_order_item)
        dining_record_item_dict = {
            "user_id": order.user_id,
            "order_id": db_order.id,
            "menu_item_id": item.menu_item_id,
            "menu_item_name": db.query(models.MenuItem).get(item.menu_item_id).en_name,
            "total_amount": db_order_item.unit_price * item.quantity,
            "payment_status": db_order.payment_status
        }
        if os.getenv("IS_TEST") != "true":
            send_order_notification(dining_record_item_dict) 
    
    db.commit()
    return db_order

@app.get("/orders/{order_id}", response_model=schemas.Order)
def get_order(
    order_id: int,
    db: Session = Depends(get_db)
):
    order = db.query(models.Order).filter(models.Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    return order

@app.get("/users/{user_id}/orders/", response_model=List[schemas.Order])
def get_user_orders(
    user_id: int,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    return db.query(models.Order).filter(
        models.Order.user_id == user_id
    ).offset(skip).limit(limit).all()

@app.put("/orders/{user_id}/status")
def update_order_status(
    user_id: int,
    status: str,
    db: Session = Depends(get_db)
):
    orders = db.query(models.Order).filter(models.Order.user_id == user_id).all()
    if not orders:
        raise HTTPException(status_code=404, detail="No orders found for this user")
    if status not in ["paid", "unpaid"]:
        raise HTTPException(status_code=400, detail="Invalid status")
    for order in orders:
        logger.info(f"Updating order {order.id} status to {status}")
        current_order_items = db.query(models.OrderItem).filter(models.OrderItem.order_id == order.id).all()
        for item in current_order_items:
            new_record_dict = {
                "user_id": user_id,
                "order_id": order.id,
                "menu_item_id": item.menu_item_id,
                "menu_item_name": db.query(models.MenuItem).get(item.menu_item_id).en_name,
                "total_amount": item.unit_price * item.quantity,
                "payment_status": status,
                "is_put": True
            }
            order.payment_status = status
            if os.getenv("IS_TEST") != "true":
                send_order_notification(new_record_dict)


router = APIRouter()

@router.get("/analytics", response_class=StreamingResponse)
def get_analytics(
    report_type: str = "order_trends", # select from "order_trends", "menu_preferences"
    report_period: str = "daily", # select from "daily", "weekly", "monthly"
    order_ids: List[int] = Query(default=None),
    db: Session = Depends(get_db)
):
    if report_type not in ["order_trends", "menu_preferences"]:
        raise HTTPException(status_code=400, detail="Invalid report type")
    if report_period not in ["daily", "weekly", "monthly"]:
        raise HTTPException(status_code=400, detail="Invalid report period")
    day_dict = {
            "daily": 1,
            "weekly": 7,
            "monthly": 30
        }
    if report_type == "order_trends":
        # Aggregate: item_id, item_name, total_quantity, total_income
        
        results = (
            db.query(
                models.MenuItem.id.label("item_id"),
                models.MenuItem.en_name.label("item_name"),
                func.sum(models.OrderItem.quantity).label("quantity"),
                func.sum(models.OrderItem.unit_price * models.OrderItem.quantity).label("income")
            )
            .join(models.OrderItem, models.MenuItem.id == models.OrderItem.menu_item_id)
            .join(models.Order, models.OrderItem.order_id == models.Order.id)
            .filter(models.Order.order_date >= (datetime.utcnow() - timedelta(days=day_dict[report_period])))
            .group_by(models.MenuItem.id, models.MenuItem.en_name)
            .order_by(func.sum(models.OrderItem.quantity).desc())
            .all()
        )

        if not results:
            raise HTTPException(status_code=404, detail="No order data found")

        # Generate CSV
        buffer = io.StringIO()
        buffer.write("item_id,item_name,quantity,income\n")
        for row in results:
            buffer.write(f"{row.item_id},{row.item_name},{row.quantity},{row.income:.2f}\n")
        buffer.seek(0)

        return StreamingResponse(
            buffer,
            media_type="text/csv",
            headers={"Content-Disposition": "attachment; filename=analytics.csv"}
        )
    elif report_type == "menu_preferences":
        if order_ids is None:
            raise HTTPException(status_code=400, detail="Order IDs must be provided for menu preferences report")
        # Define date threshold
        start_date = datetime.utcnow() - timedelta(days=day_dict[report_period])
    
        # Query how many of the given order_ids are within the time window
        recent_order_count = (
            db.query(models.Order)
            .filter(
                models.Order.id.in_(order_ids),
                models.Order.order_date >= start_date
            )
            .count()
        )
    
        # Generate CSV
        buffer = io.StringIO()
        buffer.write("total_order_ids,recent_orders_within_period\n")
        buffer.write(f"{len(order_ids)},{recent_order_count}\n")
        buffer.seek(0)
    
        return StreamingResponse(
            buffer,
            media_type="text/csv",
            headers={"Content-Disposition": "attachment; filename=menu_preferences.csv"}
        )

@app.get("/")
def root():
    return {"message": "Order service running"}
app.include_router(router, prefix="/api", tags=["Analytics"])