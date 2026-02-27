#!/bin/bash

# Calculus OOM Backend 參數化部署腳本
set -e

# 載入環境變數
if [ -f .env ]; then
    echo "載入環境變數檔案..."
    export $(grep -v '^#' .env | grep -v '^$' | xargs)
else
    echo "警告: 找不到 .env 檔案，使用預設值"
fi

# 預設值設定
DB_WAIT_TIME=${DB_WAIT_TIME:-10}
BACKEND_WAIT_TIME=${BACKEND_WAIT_TIME:-10}
BACKEND_IMAGE_NAME=${BACKEND_IMAGE_NAME:-calculus-backend}
BACKEND_CONTAINER_NAME=${BACKEND_CONTAINER_NAME:-calculus_backend}
NETWORK_NAME=${NETWORK_NAME:-calculus-project_calculus_network}
POSTGRES_CONTAINER=${POSTGRES_CONTAINER:-calculus_postgres}
MONGODB_CONTAINER=${MONGODB_CONTAINER:-calculus_mongodb}
PGADMIN_CONTAINER=${PGADMIN_CONTAINER:-calculus_pgadmin}
BACKEND_EXTERNAL_PORT=${BACKEND_EXTERNAL_PORT:-8000}
DB_EXTERNAL_PORT=${DB_EXTERNAL_PORT:-5433}
MONGO_EXTERNAL_PORT=${MONGO_EXTERNAL_PORT:-27017}
PGADMIN_EXTERNAL_PORT=${PGADMIN_EXTERNAL_PORT:-5051}

# 顏色定義
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${BLUE}🚀 Calculus OOM Backend 部署${NC}"
echo "=================================="

# 1. 啟動資料庫服務
echo -e "${YELLOW}📊 啟動資料庫服務...${NC}"
sudo docker-compose up -d postgres mongodb pgadmin

# 等待資料庫啟動
echo -e "${YELLOW}⏳ 等待資料庫啟動 (${DB_WAIT_TIME}秒)...${NC}"
sleep ${DB_WAIT_TIME}

# 2. 執行pgAdmin自動註冊
echo -e "${YELLOW}🔧 配置pgAdmin...${NC}"
sudo docker exec ${PGADMIN_CONTAINER} python /pgadmin4/pgadmin_setup.py

# 3. 構建並運行後端
echo -e "${YELLOW}📦 構建後端Docker鏡像...${NC}"
sudo docker build -t ${BACKEND_IMAGE_NAME} .

echo -e "${YELLOW}🚀 啟動後端服務...${NC}"
sudo docker run -d \
    --name ${BACKEND_CONTAINER_NAME} \
    --network ${NETWORK_NAME} \
    -p ${BACKEND_EXTERNAL_PORT}:8000 \
    -e DB_HOST=${POSTGRES_CONTAINER} \
    -e DB_PORT=5432 \
    -e DB_NAME=${DB_NAME} \
    -e DB_USER=${DB_USER} \
    -e DB_PASSWORD=${DB_PASSWORD} \
    -e MONGO_HOST=${MONGODB_CONTAINER} \
    -e MONGO_PORT=27017 \
    -e MONGO_USER=${MONGO_USER} \
    -e MONGO_PASSWORD=${MONGO_PASSWORD} \
    -e MONGO_DB=${MONGO_DB} \
    ${BACKEND_IMAGE_NAME}

# 4. 等待後端啟動
echo -e "${YELLOW}⏳ 等待後端啟動 (${BACKEND_WAIT_TIME}秒)...${NC}"
sleep ${BACKEND_WAIT_TIME}

# 5. 執行資料庫遷移
echo -e "${YELLOW}📋 執行資料庫遷移...${NC}"
sudo docker exec ${BACKEND_CONTAINER_NAME} python manage.py migrate

# 6. 驗證部署
echo -e "${YELLOW}🔍 驗證部署...${NC}"

# 檢查PostgreSQL
if sudo docker exec ${POSTGRES_CONTAINER} pg_isready -U ${DB_USER} -d ${DB_NAME} > /dev/null; then
    echo -e "${GREEN}✅ PostgreSQL: 正常運行${NC}"
else
    echo -e "${RED}❌ PostgreSQL: 連接失敗${NC}"
fi

# 檢查MongoDB
if sudo docker exec ${MONGODB_CONTAINER} mongosh --eval "db.adminCommand('ping')" > /dev/null 2>&1; then
    echo -e "${GREEN}✅ MongoDB: 正常運行${NC}"
else
    echo -e "${RED}❌ MongoDB: 連接失敗${NC}"
fi

# 檢查後端
if curl -s http://localhost:${BACKEND_EXTERNAL_PORT} > /dev/null; then
    echo -e "${GREEN}✅ Django Backend: 正常運行${NC}"
else
    echo -e "${RED}❌ Django Backend: 連接失敗${NC}"
fi

# 7. 顯示訪問信息
echo -e "\n${BLUE}🌐 服務訪問信息${NC}"
echo "=================================="
echo -e "${GREEN}Django Backend: http://localhost:${BACKEND_EXTERNAL_PORT}${NC}"
echo -e "${GREEN}pgAdmin: http://localhost:${PGADMIN_EXTERNAL_PORT}${NC}"
echo -e "  📧 Email: ${PGADMIN_EMAIL}"
echo -e "  🔑 Password: ${PGADMIN_PASSWORD}"
echo -e "${GREEN}PostgreSQL: localhost:${DB_EXTERNAL_PORT}${NC}"
echo -e "${GREEN}MongoDB: localhost:${MONGO_EXTERNAL_PORT}${NC}"

echo -e "\n${BLUE}🛠️ 管理指令${NC}"
echo "=================================="
echo "查看後端日誌: sudo docker logs -f ${BACKEND_CONTAINER_NAME}"
echo "停止服務: sudo docker-compose down && sudo docker stop ${BACKEND_CONTAINER_NAME}"
echo "重啟後端: sudo docker restart ${BACKEND_CONTAINER_NAME}"

echo -e "\n${GREEN}✅ 部署完成！${NC}"