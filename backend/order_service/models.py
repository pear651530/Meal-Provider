from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Float, Table, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime

Base = declarative_base()

order_items = Table('order_items', Base.metadata,
    Column('order_id', Integer, ForeignKey('orders.id'), primary_key=True),
    Column('menu_item_id', Integer, ForeignKey('menu_items.id'), primary_key=True),
    Column('quantity', Integer),
    Column('unit_price', Float)
)

class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer)  # Reference to User Service
    order_date = Column(DateTime, default=datetime.utcnow)
    total_amount = Column(Float)
    status = Column(String)  # pending, completed, cancelled
    payment_method = Column(String)  # cash, credit
    payment_status = Column(String)  # paid, unpaid
    
    items = relationship("MenuItem", secondary=order_items, back_populates="orders")

class MenuItem(Base):
    __tablename__ = "menu_items"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    description = Column(String)
    price = Column(Float)
    category = Column(String)
    is_available = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    orders = relationship("Order", secondary=order_items, back_populates="items") 