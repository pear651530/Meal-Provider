from pydantic import BaseModel
from typing import Optional, List, Dict
from datetime import datetime
class MenuItemCreate(BaseModel):
    ZH_name: str
    EN_name: str
    price: float
    URL: str
    is_available: bool = True

class MenuItem(MenuItemCreate):
    id: int
    created_at: datetime  # 包含創建時間
    updated_at: Optional[datetime] = None # 包含更新時間
    class Config:
        orm_mode = True

class MenuChangeBase(BaseModel):
    menu_item_id: int
    change_type: str  # "add", "update", "remove"

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
        orm_mode = True

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
        orm_mode = True

class AnalyticsBase(BaseModel):
    report_type: str  # "order_trends", "menu_preferences"
    report_period: str  # "daily", "weekly", "monthly"
    data: Dict

class Analytics(AnalyticsBase):
    id: int
    report_date: datetime
    generated_at: datetime

    class Config:
        orm_mode = True