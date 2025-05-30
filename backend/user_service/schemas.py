from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List

class UserBase(BaseModel):
    username: str

class UserCreate(UserBase):
    password: str

class User(UserBase):
    id: int
    role: str
    created_at: datetime

    class Config:
        from_attributes = True

class ReviewBase(BaseModel):
    rating: str  # "good" or "bad"
    comment: str

class ReviewCreate(ReviewBase):
    pass

class Review(ReviewBase):
    id: int
    user_id: int
    dining_record_id: int
    created_at: datetime

    class Config:
        from_attributes = True

class DiningRecordBase(BaseModel):
    order_id: int
    menu_item_id: int
    menu_item_name: str
    total_amount: float
    payment_status: str

class DiningRecordCreate(DiningRecordBase):
    pass

class DiningRecord(DiningRecordBase):
    id: int
    user_id: int
    dining_date: datetime
    reviews: List[Review] = []

    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None

class UnpaidUser(BaseModel):
    user_id: int
    user_name: str
    unpaidAmount: float

    class Config:
        from_attributes = True

class MenuItemRating(BaseModel):
    menu_item_id: int
    menu_item_name: str
    total_reviews: int  # Total number of reviews for this menu item
    good_reviews: int
    good_ratio: float  # Ratio of good reviews (good_reviews / total_reviews)

    class Config:
        from_attributes = True

class Notification(BaseModel):
    id: int
    user_id: int
    message: str
    notification_type: str
    is_read: bool
    created_at: datetime

    class Config:
        orm_mode = True 

class MenuItemRatingWithOrders(BaseModel):
    menu_item_id: int
    menu_item_name: str
    total_reviews: int  # Total number of reviews for this menu item
    good_reviews: int
    good_ratio: float  # Ratio of good reviews (good_reviews / total_reviews)
    order_ids: List[int]

    class Config:
        from_attributes = True

class MenuItemComment(BaseModel):
    comment: str
    rating: str
    created_at: datetime
    user_id: int
    username: Optional[str]

    class Config:
        from_attributes = True