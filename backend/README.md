# Meal Provider System

餐廳內部員工用餐管理系統，基於微服務架構設計。

## 系統架構

系統分為三個主要的微服務：

1. User Service (用戶服務)
   - 員工帳戶管理
   - 身分驗證
   - 用餐記錄查詢
   - 評價系統
   - 賬單通知

2. Order Service (訂單服務)
   - 點餐系統
   - 訂單管理
   - 賒帳處理

3. Admin Service (管理員服務)
   - 菜單管理
   - 餐點更新
   - 帳單管理
   - 數據分析

## 技術棧

- Backend: FastAPI
- Database: PostgreSQL
- ORM: SQLAlchemy
- Migration: Alembic
- Authentication: JWT

## 安裝與設置

1. 安裝依賴：
```bash
pip install -r requirements.txt
```

2. 設置環境變數：
創建 .env 文件並設置以下變數：
```
DATABASE_URL=postgresql://postgres:password@localhost:5432/meal_provider
SECRET_KEY=your-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

3. 初始化數據庫：
```bash
alembic upgrade head
```

4. 運行服務：
```bash
uvicorn app.main:app --reload
```

## API 文檔

啟動服務後，可以訪問以下地址查看 API 文檔：
- http://localhost:8000/docs (Swagger UI)
- http://localhost:8000/redoc (ReDoc) 