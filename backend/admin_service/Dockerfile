FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Install PostgreSQL client for pg_isready and psql
RUN apt-get update && apt-get install -y postgresql-client && rm -rf /var/lib/apt/lists/*

COPY . .
COPY /admin_start_service.sh /admin_start_service.sh
RUN chmod +x /admin_start_service.sh

CMD ["/admin_start_service.sh"] 