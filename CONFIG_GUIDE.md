# Calculus OOM Backend 配置指南

## 🔧 環境變數配置

本專案已完全參數化，所有配置都可以通過 `.env` 文件進行自訂。

### 📁 配置文件

- **`.env`** - 主要環境變數配置文件
- **`docker-compose.yaml`** - 使用環境變數的服務編排文件
- **`deploy.sh`** - 參數化部署腳本

### 🔐 安全配置（生產環境必改）

```bash
# Django 核心設定
DJANGO_SECRET_KEY=your-super-secret-key-here
DJANGO_DEBUG=False
DJANGO_ENV=production
DJANGO_ALLOWED_HOSTS=your-domain.com,localhost

# 資料庫密碼
DB_PASSWORD=your-secure-password
MONGO_PASSWORD=your-secure-password

# pgAdmin 登入
PGADMIN_EMAIL=your-admin@domain.com
PGLADMIN_PASSWORD=your-secure-password
```

### 🌐 網路配置

```bash
# 外部訪問端口
BACKEND_EXTERNAL_PORT=8000        # Django API
DB_EXTERNAL_PORT=5433             # PostgreSQL
MONGO_EXTERNAL_PORT=27017         # MongoDB  
PGLADMIN_EXTERNAL_PORT=5051        # pgAdmin

# 容器名稱
BACKEND_CONTAINER_NAME=calculus_backend
POSTGRES_CONTAINER=calculus_postgres
MONGODB_CONTAINER=calculus_mongodb
PGLADMIN_CONTAINER=calculus_pgladmin
```

### ⏱️ 時間配置

```bash
# 部署等待時間（秒）
DB_WAIT_TIME=10                   # 資料庫啟動等待
BACKEND_WAIT_TIME=10              # 後端啟動等待
```

### 🏷️ Docker 配置

```bash
# Docker 映像與網路
BACKEND_IMAGE_NAME=calculus-backend
NETWORK_NAME=calculus-project_calculus_network
```

## 🚀 使用方式

### 1. 自訂配置
```bash
# 編輯配置文件
vim .env

# 修改你需要的參數
BACKEND_EXTERNAL_PORT=9000
DB_EXTERNAL_PORT=5434
PGLADMIN_PASSWORD=my-secure-password
```

### 2. 部署系統
```bash
# 一鍵部署（自動讀取 .env 配置）
./deploy.sh
```

### 3. 驗證部署
```bash
# 系統會自動顯示實際的訪問地址
# 例如：Django Backend: http://localhost:9000
```

## 🔄 配置變更流程

### 更改端口範例
```bash
# 1. 停止現有服務
sudo docker-compose down
sudo docker stop ${BACKEND_CONTAINER_NAME}

# 2. 修改 .env 文件
echo "BACKEND_EXTERNAL_PORT=9000" >> .env

# 3. 重新部署
./deploy.sh
```

### 更改密碼範例
```bash
# 1. 修改 .env 文件中的密碼
DB_PASSWORD=new-secure-password
MONGO_PASSWORD=new-secure-password

# 2. 清理現有資料（注意：會刪除所有資料）
sudo docker-compose down -v

# 3. 重新部署
./deploy.sh
```

## 🔍 配置驗證

### 檢查實際配置
```bash
# 查看 docker-compose 實際配置
sudo docker-compose config

# 查看容器環境變數
sudo docker exec ${BACKEND_CONTAINER_NAME} env | grep -E "(DB_|MONGO_)"
```

### 檢查服務狀態
```bash
# 檢查所有服務
sudo docker ps

# 檢查網路配置
sudo docker network ls
sudo docker network inspect ${NETWORK_NAME}
```

## ⚠️ 注意事項

1. **生產環境安全**：
   - 必須更改預設密碼
   - 設定 `DJANGO_DEBUG=False`
   - 限制 `DJANGO_ALLOWED_HOSTS`

2. **端口衝突**：
   - 確保選擇的端口未被佔用
   - 使用 `netstat -tulpn` 檢查端口使用情況

3. **資料持久化**：
   - Docker volumes 會保存資料
   - 使用 `docker-compose down -v` 會刪除所有資料

4. **網路配置**：
   - 容器間通訊使用內部網路
   - 外部訪問通過映射端口

## 📋 常用配置範例

### 開發環境
```bash
DJANGO_DEBUG=True
BACKEND_EXTERNAL_PORT=8000
DB_EXTERNAL_PORT=5433
```

### 測試環境  
```bash
DJANGO_DEBUG=True
BACKEND_EXTERNAL_PORT=8001
DB_EXTERNAL_PORT=5434
BACKEND_CONTAINER_NAME=calculus_backend_test
```

### 生產環境
```bash
DJANGO_DEBUG=False
DJANGO_ENV=production
DJANGO_ALLOWED_HOSTS=api.yourdomain.com
BACKEND_EXTERNAL_PORT=80
DB_EXTERNAL_PORT=5432
```

這樣的參數化配置讓系統部署更加靈活且安全！