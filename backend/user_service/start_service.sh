#!/bin/sh
set -e

# Default values if not set
: "${POSTGRES_HOST:=postgres-user}"
: "${POSTGRES_USER:=postgres}"
: "${POSTGRES_PASSWORD:=password}"
: "${POSTGRES_DB:=meal_provider_user}"

# Wait for PostgreSQL to be ready
until pg_isready -h $POSTGRES_HOST -U $POSTGRES_USER -d $POSTGRES_DB; do
  echo "Waiting for PostgreSQL to be ready..."
  sleep 2
done

echo "Initializing database..."
# python -c "from user_service.init_db import init_db; init_db()"
python -c "from init_db import init_db; init_db()"

echo "Waiting for users table to be ready..."

until PGPASSWORD=$POSTGRES_PASSWORD psql -h $POSTGRES_HOST -U $POSTGRES_USER -d $POSTGRES_DB -c "SELECT 1 FROM users LIMIT 1;" > /dev/null 2>&1; do
  echo "users table not ready, waiting..."
  sleep 2
done

echo "users table is ready, starting FastAPI..."
# exec uvicorn user_service.main:app --host 0.0.0.0 --port 8000 
exec uvicorn main:app --host 0.0.0.0 --port 8000 