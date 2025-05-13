from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
import requests
from datetime import datetime, timedelta

from . import models, schemas, database
from .database import get_db

app = FastAPI(title="Admin Service API")

# 其他服務的URL（在k8s中會通過服務發現來獲取）
USER_SERVICE_URL = "http://user-service:8000"
ORDER_SERVICE_URL = "http://order-service:8000"

# 驗證管理員權限的依賴
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

# 菜單變更相關路由
@app.post("/menu-changes/", response_model=schemas.MenuChange)
async def create_menu_change(
    menu_change: schemas.MenuChangeCreate,
    db: Session = Depends(get_db),
    admin: dict = Depends(verify_admin)
):
    db_menu_change = models.MenuChange(
        **menu_change.dict(),
        changed_by=admin["id"]
    )
    db.add(db_menu_change)
    db.commit()
    db.refresh(db_menu_change)
    
    # 更新訂單服務中的菜單項目
    try:
        requests.put(
            f"{ORDER_SERVICE_URL}/menu-items/{menu_change.menu_item_id}",
            json=menu_change.new_values
        )
    except requests.RequestException:
        # 記錄錯誤但不中斷操作
        pass
    
    return db_menu_change

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
    for user_id, orders in groupby(unpaid_orders, key=lambda x: x["user_id"]):
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
    report_type: str = None,
    db: Session = Depends(get_db),
    admin: dict = Depends(verify_admin)
):
    query = db.query(models.Analytics)
    if report_type:
        query = query.filter(models.Analytics.report_type == report_type)
    return query.all() 