from fastapi import FastAPI, Depends, HTTPException, APIRouter
from sqlalchemy.orm import Session
from typing import List
import requests
from datetime import datetime
from fastapi.responses import StreamingResponse
import io
from sqlalchemy import func

from . import models, schemas, database
from .database import get_db

from .rabbitmq import *

app = FastAPI(title="Order Service API")

# 用戶服務URL（在k8s中會通過服務發現來獲取）
USER_SERVICE_URL = "http://user-service:8000"

consumer_thread = None

@app.on_event("startup")
async def startup_event():
    """Initialize services on startup"""
    global consumer_thread
    # Set up RabbitMQ
    setup_rabbitmq()
    # Get a database session
    db = next(get_db())
    try:
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
            raise HTTPException(status_code=400, detail=f"Menu item {menu_item.EN_name} is not available")
        total_amount += menu_item.price * item.quantity

    # 創建訂單
    db_order = models.Order(
        user_id=order.user_id,
        total_amount=total_amount,
        payment_method=order.payment_method,
        status=order.status,
        payment_status=order.payment_status
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

@app.put("/orders/{order_id}/status")
def update_order_status(
    order_id: int,
    status: str,
    db: Session = Depends(get_db)
):
    order = db.query(models.Order).filter(models.Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    
    order.status = status
    db.commit()
    return {"message": "Order status updated successfully"} 

router = APIRouter()

@router.get("/analytics", response_class=StreamingResponse)
def get_analytics(db: Session = Depends(get_db)):
    # Aggregate: item_id, item_name, total_quantity, total_income
    results = (
        db.query(
            models.MenuItem.id.label("item_id"),
            models.MenuItem.EN_name.label("item_name"),
            func.sum(models.OrderItem.quantity).label("quantity"),
            func.sum(models.OrderItem.unit_price * models.OrderItem.quantity).label("income")
        )
        .join(models.OrderItem, models.MenuItem.id == models.OrderItem.menu_item_id)
        .join(models.Order, models.OrderItem.order_id == models.Order.id)
        .group_by(models.MenuItem.id, models.MenuItem.EN_name)
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
    
app.include_router(router, prefix="/api", tags=["Analytics"])

@app.get("/")
def root():
    return {"message": "Order service running"}