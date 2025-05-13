from pydantic import BaseModel
from datetime import datetime
from typing import List, Optional

class MenuItemBase(BaseModel):
    name: str
    description: str
    price: float
    category: str
    is_available: bool = True

class MenuItemCreate(MenuItemBase):
    pass

class MenuItem(MenuItemBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class OrderItemBase(BaseModel):
    menu_item_id: int
    quantity: int
    unit_price: float

class OrderItemCreate(OrderItemBase):
    pass

class OrderItem(OrderItemBase):
    order_id: int

    class Config:
        from_attributes = True

class OrderBase(BaseModel):
    user_id: int
    payment_method: str
    status: str = "pending"
    payment_status: str = "unpaid"

class OrderCreate(OrderBase):
    items: List[OrderItemCreate]

class Order(OrderBase):
    id: int
    order_date: datetime
    total_amount: float
    items: List[OrderItem] = []

    class Config:
        from_attributes = True 