from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List

class UserBase(BaseModel):
    username: str
    full_name: str

class UserCreate(UserBase):
    password: str

class User(UserBase):
    id: int
    role: str
    created_at: datetime

    class Config:
        from_attributes = True

class ReviewBase(BaseModel):
    rating: int
    comment: str

class ReviewCreate(ReviewBase):
    dining_record_id: int

class Review(ReviewBase):
    id: int
    user_id: int
    created_at: datetime

    class Config:
        from_attributes = True

class DiningRecordBase(BaseModel):
    order_id: int
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