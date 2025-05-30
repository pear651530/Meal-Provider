from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Float, JSON, Table, Boolean
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime
from sqlalchemy.orm import relationship

Base = declarative_base()

# ====================================================================
# [註解] 翻譯相關的關聯表和模型。如果未來需要多語言，可以取消註解並重新設計。
# menu_item_translations_association = Table(
#     "menu_item_translations_association",
#     Base.metadata,
#     Column("menu_item_id", ForeignKey("menu_items.id"), primary_key=True),
#     Column("menu_item_translation_id", ForeignKey("menu_item_translations.id"), primary_key=True),
# )
# ====================================================================

class MenuItem(Base):
    """
    菜單項目模型：定義了菜單中單一餐點的屬性。
    直接包含中英文名稱，方便處理。
    """
    __tablename__ = "menu_items"
    id = Column(Integer, primary_key=True, index=True)
    zh_name = Column(String, nullable=False)
    en_name = Column(String, nullable=False)
    url = Column(String, nullable=True)     
    is_available = Column(Boolean, default=True) # 是否可用，預設為 True
    price = Column(Float, nullable=False)   
    created_at = Column(DateTime, default=datetime.utcnow) # 創建時間
    updated_at = Column(DateTime, onupdate=datetime.utcnow) # 更新時間，每次更新時自動變更
    # --- 新增軟刪除欄位 ---
    is_deleted = Column(Boolean, default=False) # 新增欄位，用於軟刪除，預設為 False
    deleted_at = Column(DateTime, nullable=True) # 記錄刪除時間，預設為 NULL
    # ----------------------

    # 定義與 MenuChange 的一對多關係，一個菜單項目可以有多個變更記錄
    menu_changes = relationship("MenuChange", back_populates="menu_item")

    # ====================================================================
    # [註解] 翻譯相關的關係。
    # translations = relationship("MenuItemTranslation", secondary=menu_item_translations_association, back_populates="menu_items")
    # ====================================================================


class MenuChange(Base):
    """
    菜單變更記錄模型：追蹤菜單項目的所有修改歷史。
    """
    __tablename__ = "menu_changes"

    id = Column(Integer, primary_key=True, index=True)
    # 這裡的 Foreign Key 關係可以保留，因為 MenuItem 記錄不會被真正刪除
    # menu_item_id 可以保持為 NOT NULL，因為它會指向一個真實存在的 MenuItem (只是可能被標記為 deleted)
    menu_item_id = Column(Integer, ForeignKey("menu_items.id"), nullable=False) # 確保這裡不是 nullable=True
    
    change_type = Column(String, nullable=False) # 變更類型："add", "update", "soft_remove", "toggle_availability"
    
    old_values = Column(JSON, nullable=True) # 記錄舊值 (變更前狀態)，可為空 (例如新增時)
    new_values = Column(JSON, nullable=False) # 記錄新值 (變更後狀態)，不可為空

    changed_by = Column(Integer, nullable=False) # 執行變更的管理員 ID
    changed_at = Column(DateTime, default=datetime.utcnow) # 變更發生的時間

    # 定義與 MenuItem 的多對一關係
    menu_item = relationship("MenuItem", back_populates="menu_changes")


# ====================================================================
# [註解] 翻譯相關的模型。
# class MenuItemTranslation(Base):
#     __tablename__ = "menu_item_translations"

#     id = Column(Integer, primary_key=True, index=True)
#     language = Column(String, nullable=False) # 'zh-TW', 'en-US'
#     name = Column(String)
#     description = Column(String)

#     menu_items = relationship("MenuItem", secondary=menu_item_translations_association, back_populates="translations")
# ====================================================================
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
