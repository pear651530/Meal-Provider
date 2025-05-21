from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Float
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
    full_name = Column(String)
    role = Column(String)  # employee or admin
    created_at = Column(DateTime, default=datetime.utcnow)
    
    dining_records = relationship("DiningRecord", back_populates="user")
    reviews = relationship("Review", back_populates="user")

class DiningRecord(Base):
    __tablename__ = "dining_records"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    order_id = Column(Integer)  # Reference to Order Service
    dining_date = Column(DateTime, default=datetime.utcnow)
    total_amount = Column(Float)
    payment_status = Column(String)  # paid or credit
    
    user = relationship("User", back_populates="dining_records")
    reviews = relationship("Review", back_populates="dining_record")

class Review(Base):
    __tablename__ = "reviews"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    dining_record_id = Column(Integer, ForeignKey("dining_records.id"))
    rating = Column(Integer)  # 1-5
    comment = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    user = relationship("User", back_populates="reviews")
    dining_record = relationship("DiningRecord", back_populates="reviews") 