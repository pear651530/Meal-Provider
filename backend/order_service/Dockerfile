FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY order_service/ ./order_service/

CMD ["uvicorn", "order_service.main:app", "--host", "0.0.0.0", "--port", "8000"] 