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

# 檢查命令是否存在
check_command() {
    if ! command -v $1 &> /dev/null; then
        print_error "$1 is not installed"
        exit 1
    fi
}

# 等待 Pod 就緒
wait_for_pod() {
    local pod_label=$1
    local namespace=$2
    local timeout=$3
    
    print_info "Waiting for pod with label $pod_label to be ready..."
    if ! kubectl wait --for=condition=ready pod -l $pod_label -n $namespace --timeout=${timeout}s; then
        print_error "Pod with label $pod_label failed to become ready within ${timeout}s"
        exit 1
    fi
}

# 檢查必要的命令
print_info "Checking required commands..."
check_command kubectl
check_command docker
check_command helm

# 創建命名空間
print_info "Creating namespace..."
kubectl create namespace meal-provider --dry-run=client -o yaml | kubectl apply -f -

# 部署資源配額
print_info "Deploying resource quotas..."
kubectl apply -f ../quotas/namespace-quota.yaml

# 部署數據庫
print_info "Deploying databases..."
kubectl apply -f ../database/postgres-config.yaml
kubectl apply -f ../database/postgres-services.yaml
kubectl apply -f ../database/postgres-user-statefulset.yaml
kubectl apply -f ../database/postgres-order-statefulset.yaml
kubectl apply -f ../database/postgres-admin-statefulset.yaml

# 等待數據庫就緒
wait_for_pod "app=postgres-user" "meal-provider" 300
wait_for_pod "app=postgres-order" "meal-provider" 300
wait_for_pod "app=postgres-admin" "meal-provider" 300

# 部署 RabbitMQ
print_info "Deploying RabbitMQ..."
kubectl apply -f ../rabbitmq/rabbitmq-config.yaml
kubectl apply -f ../rabbitmq/rabbitmq-statefulset.yaml
kubectl apply -f ../rabbitmq/rabbitmq-service.yaml

# 等待 RabbitMQ 就緒
wait_for_pod "app=rabbitmq" "meal-provider" 180

# 部署後端服務
print_info "Deploying backend services..."
kubectl apply -f ../backend/backend-config.yaml
kubectl apply -f ../backend/user-service.yaml
kubectl apply -f ../backend/order-service.yaml
kubectl apply -f ../backend/admin-service.yaml

# 等待後端服務就緒
wait_for_pod "app=user-service" "meal-provider" 120
wait_for_pod "app=order-service" "meal-provider" 120
wait_for_pod "app=admin-service" "meal-provider" 120

# 部署前端服務
print_info "Deploying frontend..."
kubectl apply -f ../frontend/frontend-config.yaml
kubectl apply -f ../frontend/frontend-deployment.yaml
kubectl apply -f ../frontend/frontend-ingress.yaml

# 等待前端就緒
wait_for_pod "app=frontend" "meal-provider" 120

# 部署監控系統
print_info "Deploying monitoring system..."
kubectl apply -f ../monitoring/prometheus-config.yaml
kubectl apply -f ../monitoring/prometheus-deployment.yaml
kubectl apply -f ../monitoring/grafana-deployment.yaml
kubectl apply -f ../monitoring/grafana-ingress.yaml

# 等待監控系統就緒
wait_for_pod "app=prometheus" "meal-provider" 120
wait_for_pod "app=grafana" "meal-provider" 120

# 部署 HPA
print_info "Deploying HPA..."
kubectl apply -f ../hpa/user-service-hpa.yaml
kubectl apply -f ../hpa/order-service-hpa.yaml
kubectl apply -f ../hpa/frontend-hpa.yaml

# 部署備份配置
print_info "Deploying backup configurations..."
kubectl apply -f ../backup/backup-config.yaml
kubectl apply -f ../backup/backup-cronjob.yaml

print_info "Deployment completed successfully!"
print_info "You can access the following services:"
print_info "- Frontend: http://localhost"
print_info "- Grafana Dashboard: http://localhost:3000"
print_info "- Prometheus: http://localhost:9090"
print_info "- RabbitMQ Management: http://localhost:15672" 