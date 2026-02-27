#!/bin/bash

# Calculus OOM Backend 簡化部署腳本
set -e

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
echo -e "${YELLOW}⏳ 等待資料庫啟動 (30秒)...${NC}"
sleep 30

# 2. 執行pgAdmin自動註冊
echo -e "${YELLOW}🔧 配置pgAdmin...${NC}"
sudo docker exec calculus_pgadmin python /pgadmin4/pgadmin_setup.py

# 3. 構建並運行後端
echo -e "${YELLOW}📦 構建後端Docker鏡像...${NC}"
sudo docker build -t calculus-backend .

echo -e "${YELLOW}🚀 啟動後端服務...${NC}"
sudo docker run -d \
    --name calculus_backend \
    --network calculus-project_calculus_network \
    -p 8000:8000 \
    -e DB_HOST=calculus_postgres \
    -e DB_PORT=5432 \
    -e DB_NAME=calculus_db \
    -e DB_USER=calculus_user \
    -e DB_PASSWORD=calculus_password123 \
    -e MONGO_HOST=calculus_mongodb \
    -e MONGO_PORT=27017 \
    -e MONGO_USER=calculus_user \
    -e MONGO_PASSWORD=calculus_password123 \
    -e MONGO_DB=calculus_nosql_db \
    calculus-backend

# 4. 等待後端啟動
echo -e "${YELLOW}⏳ 等待後端啟動 (10秒)...${NC}"
sleep 10

# 5. 執行資料庫遷移
echo -e "${YELLOW}📋 執行資料庫遷移...${NC}"
sudo docker exec calculus_backend python manage.py migrate

# 6. 驗證部署
echo -e "${YELLOW}🔍 驗證部署...${NC}"

# 檢查PostgreSQL
if sudo docker exec calculus_postgres pg_isready -U calculus_user -d calculus_db > /dev/null; then
    echo -e "${GREEN}✅ PostgreSQL: 正常運行${NC}"
else
    echo -e "${RED}❌ PostgreSQL: 連接失敗${NC}"
fi

# 檢查MongoDB
if sudo docker exec calculus_mongodb mongosh --eval "db.adminCommand('ping')" > /dev/null 2>&1; then
    echo -e "${GREEN}✅ MongoDB: 正常運行${NC}"
else
    echo -e "${RED}❌ MongoDB: 連接失敗${NC}"
fi

# 檢查後端
if curl -s http://localhost:8000 > /dev/null; then
    echo -e "${GREEN}✅ Django Backend: 正常運行${NC}"
else
    echo -e "${RED}❌ Django Backend: 連接失敗${NC}"
fi

# 7. 顯示訪問信息
echo -e "\n${BLUE}🌐 服務訪問信息${NC}"
echo "=================================="
echo -e "${GREEN}Django Backend: http://localhost:8000${NC}"
echo -e "${GREEN}pgAdmin: http://localhost:5051${NC}"
echo -e "  📧 Email: admin@calculus.com"
echo -e "  🔑 Password: admin123"
echo -e "${GREEN}PostgreSQL: localhost:5433${NC}"
echo -e "${GREEN}MongoDB: localhost:27017${NC}"

echo -e "\n${BLUE}🛠️ 管理指令${NC}"
echo "=================================="
echo "查看後端日誌: sudo docker logs -f calculus_backend"
echo "停止服務: sudo docker-compose down && sudo docker stop calculus_backend"
echo "重啟後端: sudo docker restart calculus_backend"

echo -e "\n${GREEN}✅ 部署完成！${NC}"