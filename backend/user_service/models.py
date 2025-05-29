from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Float, Boolean, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime

Base = declarative_base()

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    # email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    role = Column(String, default="employee")   # employee, clerk, admin, super_admin
    created_at = Column(DateTime, default=datetime.utcnow)
    
    dining_records = relationship("DiningRecord", back_populates="user")
    reviews = relationship("Review", back_populates="user")
    notifications = relationship("Notification", back_populates="user")

class DiningRecord(Base):
    __tablename__ = "dining_records"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    order_id = Column(Integer)  # Reference to Order Service
    menu_item_id = Column(Integer)  # Reference to Menu Item in Admin Service
    menu_item_name = Column(String)  # Name of the menu item
    dining_date = Column(DateTime, default=datetime.utcnow)
    total_amount = Column(Float)
    payment_status = Column(String)  # paid or unpaid
    
    user = relationship("User", back_populates="dining_records")
    review = relationship("Review", back_populates="dining_record", uselist=False)

class Review(Base):
    __tablename__ = "reviews"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    dining_record_id = Column(Integer, ForeignKey("dining_records.id"))
    rating = Column(String)  # "good" or "bad"
    comment = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    user = relationship("User", back_populates="reviews")
    dining_record = relationship("DiningRecord", back_populates="review")

class Notification(Base):
    __tablename__ = "notifications"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    message = Column(String)
    notification_type = Column(String)  # e.g., "billing", "system", etc.
    is_read = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    user = relationship("User", back_populates="notifications") 