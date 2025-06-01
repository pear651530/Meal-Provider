#!/bin/sh
set -e

# Default values for admin service database
# 注意：這些變數名和值應該與您的 docker-compose.yml 中 postgres-admin 的環境變數匹配
: "${POSTGRES_HOST:=postgres-admin}"
: "${POSTGRES_USER:=postgres}"
: "${POSTGRES_PASSWORD:=password}" # <-- 修正這裡，與 docker-compose.yml 一致
: "${POSTGRES_DB:=meal_provider_admin}"

# Wait for PostgreSQL to be ready FIRST
echo "Waiting for admin-service PostgreSQL to be ready..."
until pg_isready -h $POSTGRES_HOST -U $POSTGRES_USER -d $POSTGRES_DB; do
  echo "PostgreSQL not ready, waiting..."
  sleep 2
done
echo "PostgreSQL is ready."

# Now, initialize database tables
echo "Initializing admin-service database tables..."
# 切換到 admin_service 目錄，這樣 init_db.py 就能正確找到同級的 database 和 models
# (cd /app/admin_service && python init_db.py) # 使用子shell執行
(cd /app && python init_db.py)
echo "Admin-service database tables created/ensured."

# Wait for menu_items table to be ready (optional, but good for robustness)
echo "Debugging menu_items table check..."
until PGPASSWORD=$POSTGRES_PASSWORD psql -h $POSTGRES_HOST -U $POSTGRES_USER -d $POSTGRES_DB -c "SELECT 1 FROM menu_items LIMIT 1;"; do
  # 移除 > /dev/null 2>&1，讓錯誤訊息能顯示在控制台
  echo "menu_items table check failed, retrying in 2 seconds..."
  sleep 2
done
echo "menu_items table is ready." # 或者 "menu_items table check succeeded."

echo "Starting FastAPI for admin-service..."
# 確保這裡的路徑指向 admin_service 的 main.py 和 app 對象
exec uvicorn main:app --host 0.0.0.0 --port 8000