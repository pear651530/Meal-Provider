from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Float, JSON, Table, Boolean
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime
from sqlalchemy.orm import relationship

Base = declarative_base()

# 關聯表，用於 MenuItem 和 MenuItemTranslation 之間的多對多關係
menu_item_translations_association = Table(
    "menu_item_translations_association",
    Base.metadata,
    Column("menu_item_id", ForeignKey("menu_items.id"), primary_key=True),
    Column("menu_item_translation_id", ForeignKey("menu_item_translations.id"), primary_key=True),
)

class MenuChange(Base):
    __tablename__ = "menu_changes"

    id = Column(Integer, primary_key=True, index=True)
    menu_item_id = Column(Integer, ForeignKey("menu_items.id"))  # Reference to Order Service MenuItem
    change_type = Column(String)  # "add", "update", "remove"
    # 修改這裡：將 changed_fields 拆分為 old_values 和 new_values
    old_values = Column(JSON, nullable=True) # 記錄舊值
    new_values = Column(JSON, nullable=False) # 記錄新值
    changed_by = Column(Integer)  # Reference to User Service admin
    changed_at = Column(DateTime, default=datetime.utcnow)

    menu_item = relationship("MenuItem", back_populates="menu_changes")
class BillingNotification(Base):
    __tablename__ = "billing_notifications"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer)  # Reference to User Service
    total_amount = Column(Float)
    billing_period_start = Column(DateTime)
    billing_period_end = Column(DateTime)
    status = Column(String)  # "sent", "viewed", "paid"
    sent_at = Column(DateTime, default=datetime.utcnow)
    paid_at = Column(DateTime, nullable=True)

class Analytics(Base):
    __tablename__ = "analytics"

    id = Column(Integer, primary_key=True, index=True)
    report_type = Column(String)  # "order_trends", "menu_preferences"
    report_period = Column(String)  # "daily", "weekly", "monthly"
    report_date = Column(DateTime)
    data = Column(JSON)
    generated_at = Column(DateTime, default=datetime.utcnow)

class MenuItem(Base): # 這個 model 放在這裡，是因為它和 MenuChange 有關聯
    __tablename__ = "menu_items"

    id = Column(Integer, primary_key=True, index=True)
    # 其他菜品欄位，例如 name, description, price, category 等
    #name = Column(String)
    ZH_name = Column(String)
    EN_name = Column(String)
    URL = Column(String)  # 圖片 URL
    is_available = Column(Boolean, default=True)  # 是否可用
    #description = Column(String)
    price = Column(Float)
    #category = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)  # 新增創建時間
    updated_at = Column(DateTime, onupdate=datetime.utcnow) # 可選：新增更新時間

    menu_changes = relationship("MenuChange", back_populates="menu_item")
    translations = relationship("MenuItemTranslation", secondary=menu_item_translations_association, back_populates="menu_items")

class MenuItemTranslation(Base):
    __tablename__ = "menu_item_translations"

    id = Column(Integer, primary_key=True, index=True)
    language = Column(String, nullable=False) # 'zh-TW', 'en-US'
    name = Column(String)
    description = Column(String)

    menu_items = relationship("MenuItem", secondary=menu_item_translations_association, back_populates="translations")