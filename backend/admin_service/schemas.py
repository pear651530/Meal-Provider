from pydantic import BaseModel
from typing import Optional, List, Dict
from datetime import datetime
class MenuItemCreate(BaseModel):
    zh_name: str
    en_name: str
    price: float
    url: str
    is_available: bool = True
    # --- 新增軟刪除欄位到 Pydantic Schema，用於回應 ---
    # 通常創建時不會設定 is_deleted 或 deleted_at，它們會有預設值
    # 但如果需要從 API 接收這些狀態來創建，可以添加到這裡。
    # 這裡我們只將它們添加到響應模型中。

class MenuItem(MenuItemCreate):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    # --- 新增軟刪除欄位 ---
    is_deleted: bool
    deleted_at: Optional[datetime] = None
    # ----------------------
    class Config:
        from_attributes = True

class MenuChangeBase(BaseModel):
    menu_item_id: int
    change_type: str  # "add", "update", "soft_remove","toggle_availability" # 這裡的 "hard_remove" 改為 "soft_remove"

class MenuChangeCreate(MenuChangeBase):
    old_values: Optional[Dict] = None
    new_values: Dict

class MenuChange(MenuChangeBase):
    id: int
    changed_by: int
    changed_at: datetime
    old_values: Optional[Dict] = None
    new_values: Dict

    class Config:
        from_attributes = True

class BillingNotificationBase(BaseModel):
    user_id: int
    total_amount: float
    billing_period_start: datetime
    billing_period_end: datetime
    status: str  # "sent", "viewed", "paid"

class BillingNotification(BillingNotificationBase):
    id: int
    sent_at: datetime
    paid_at: Optional[datetime]

    class Config:
        from_attributes = True

class AnalyticsBase(BaseModel):
    report_type: str  # "order_trends",   # ("menu_preferences")暫不開放使用此參數固定只能order_trend
    report_period: str  # "daily", "weekly", "monthly"
    data: Dict

class Analytics(AnalyticsBase):
    id: int
    report_date: datetime
    generated_at: datetime

    class Config:
        from_attributes = True

class UnpaidUser(BaseModel):
    id: int
    username: str
    unpaid_amount: float

    class Config:
        from_attributes = True

class AdminUser(BaseModel):
    id: int
    username: str
    role: str
    token: str

    class Config:
        from_attributes = True