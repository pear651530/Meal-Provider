FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

RUN pip install googletrans==4.0.0rc1 # 新增
RUN pip install requests

COPY admin_service/ ./admin_service/

CMD ["uvicorn", "admin_service.main:app", "--host", "0.0.0.0", "--port", "8000"]

#FROM python:3.9-slim
#WORKDIR /app
#RUN pip install --no-cache-dir requests
#CMD ["python", "-c", "import requests; print('requests installed successfully')"]