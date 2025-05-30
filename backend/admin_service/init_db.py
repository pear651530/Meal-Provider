# admin_service/init_db.py
from database import engine
from models import Base
# ----------------------------------------------------------------------
# 關鍵修改：明確導入所有你想要創建的表所對應的模型類
from models import MenuItem, MenuChange, BillingNotification, Analytics
# ----------------------------------------------------------------------

def init_db():
    print("Creating database tables...")
    Base.metadata.drop_all(bind=engine)  # 清除舊的表,for testing stage 
    Base.metadata.create_all(bind=engine)
    print("Database tables created successfully!")

if __name__ == "__main__":
    init_db()