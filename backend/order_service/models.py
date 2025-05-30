from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Float, Table, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime

Base = declarative_base()

"""
order_items = Table('order_items', Base.metadata,
    Column('order_id', Integer, ForeignKey('orders.id'), primary_key=True),
    Column('menu_item_id', Integer, ForeignKey('menu_items.id'), primary_key=True),
    Column('quantity', Integer),
    Column('unit_price', Float)
)
"""

class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer)  # Reference to User Service
    order_date = Column(DateTime, default=datetime.utcnow)
    total_amount = Column(Float)
    payment_method = Column(String)  # cash, credit
    payment_status = Column(String)  # paid, unpaid
    
    #items = relationship("MenuItem", secondary=order_items, back_populates="orders")
    order_items = relationship("OrderItem", back_populates="order")

class MenuItem(Base):
    __tablename__ = "menu_items"

    id = Column(Integer, primary_key=True, index=True)
    # name = Column(String)
    zh_name = Column(String)
    en_name = Column(String)
    url = Column(String)  # Image URL or other resource link
    # description = Column(String)
    price = Column(Float)
    # category = Column(String)
    is_available = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    #orders = relationship("Order", secondary=order_items, back_populates="items") 
    order_items = relationship("OrderItem", back_populates="menu_item")

class OrderItem(Base):
    __tablename__ = "order_items"

    order_id = Column(Integer, ForeignKey("orders.id"), primary_key=True)
    menu_item_id = Column(Integer, ForeignKey("menu_items.id"), primary_key=True)
    quantity = Column(Integer)
    unit_price = Column(Float)

    order = relationship("Order", back_populates="order_items")
    menu_item = relationship("MenuItem", back_populates="order_items")