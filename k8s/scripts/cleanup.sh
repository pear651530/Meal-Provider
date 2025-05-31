#!/bin/bash

# 設置錯誤時退出
set -e

# 顏色定義
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

# 打印帶顏色的信息
print_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 確認刪除
read -p "Are you sure you want to delete all resources in the meal-provider namespace? (y/N) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]
then
    print_info "Operation cancelled"
    exit 1
fi

# 刪除所有資源
print_info "Deleting all resources in meal-provider namespace..."

# 刪除 HPA
print_info "Deleting HPA configurations..."
kubectl delete -f ../hpa/user-service-hpa.yaml --ignore-not-found
kubectl delete -f ../hpa/order-service-hpa.yaml --ignore-not-found
kubectl delete -f ../hpa/frontend-hpa.yaml --ignore-not-found

# 刪除監控系統
print_info "Deleting monitoring system..."
kubectl delete -f ../monitoring/prometheus-config.yaml --ignore-not-found
kubectl delete -f ../monitoring/prometheus-deployment.yaml --ignore-not-found
kubectl delete -f ../monitoring/grafana-deployment.yaml --ignore-not-found
kubectl delete -f ../monitoring/grafana-ingress.yaml --ignore-not-found

# 刪除前端服務
print_info "Deleting frontend..."
kubectl delete -f ../frontend/frontend-config.yaml --ignore-not-found
kubectl delete -f ../frontend/frontend-deployment.yaml --ignore-not-found
kubectl delete -f ../frontend/frontend-ingress.yaml --ignore-not-found

# 刪除後端服務
print_info "Deleting backend services..."
kubectl delete -f ../backend/backend-config.yaml --ignore-not-found
kubectl delete -f ../backend/user-service.yaml --ignore-not-found
kubectl delete -f ../backend/order-service.yaml --ignore-not-found
kubectl delete -f ../backend/admin-service.yaml --ignore-not-found

# 刪除 RabbitMQ
print_info "Deleting RabbitMQ..."
kubectl delete -f ../rabbitmq/rabbitmq-config.yaml --ignore-not-found
kubectl delete -f ../rabbitmq/rabbitmq-statefulset.yaml --ignore-not-found
kubectl delete -f ../rabbitmq/rabbitmq-service.yaml --ignore-not-found

# 刪除 Redis
print_info "Deleting Redis..."
kubectl delete -f ../cache/redis-deployment.yaml --ignore-not-found
kubectl delete -f ../cache/redis-service.yaml --ignore-not-found

# 刪除數據庫
print_info "Deleting databases..."
kubectl delete -f ../database/postgres-config.yaml --ignore-not-found
kubectl delete -f ../database/postgres-user-statefulset.yaml --ignore-not-found
kubectl delete -f ../database/postgres-order-statefulset.yaml --ignore-not-found
kubectl delete -f ../database/postgres-admin-statefulset.yaml --ignore-not-found

# 刪除備份配置
print_info "Deleting backup configurations..."
kubectl delete -f ../backup/backup-config.yaml --ignore-not-found
kubectl delete -f ../backup/backup-cronjob.yaml --ignore-not-found

# 刪除資源配額
print_info "Deleting resource quotas..."
kubectl delete -f ../quotas/namespace-quota.yaml --ignore-not-found

# 刪除命名空間
print_info "Deleting namespace..."
kubectl delete namespace meal-provider --ignore-not-found

print_info "Cleanup completed successfully!" 