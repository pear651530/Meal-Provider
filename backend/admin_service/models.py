from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Float, JSON
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()

class MenuChange(Base):
    __tablename__ = "menu_changes"

    id = Column(Integer, primary_key=True, index=True)
    menu_item_id = Column(Integer)  # Reference to Order Service MenuItem
    change_type = Column(String)  # add, update, remove
    old_values = Column(JSON)
    new_values = Column(JSON)
    changed_by = Column(Integer)  # Reference to User Service admin
    changed_at = Column(DateTime, default=datetime.utcnow)

class BillingNotification(Base):
    __tablename__ = "billing_notifications"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer)  # Reference to User Service
    total_amount = Column(Float)
    billing_period_start = Column(DateTime)
    billing_period_end = Column(DateTime)
    status = Column(String)  # sent, viewed, paid
    sent_at = Column(DateTime, default=datetime.utcnow)
    paid_at = Column(DateTime, nullable=True)

class Analytics(Base):
    __tablename__ = "analytics"

    id = Column(Integer, primary_key=True, index=True)
    report_type = Column(String)  # order_trends, menu_preferences
    report_period = Column(String)  # daily, weekly, monthly
    report_date = Column(DateTime)
    data = Column(JSON)
    generated_at = Column(DateTime, default=datetime.utcnow) 