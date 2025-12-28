# Calculus OOM Backend

微積分考卷、學生管理系統後端 API

## 專案結構

```
backend/
├── main/
│   ├── settings/           # 環境配置
│   │   ├── base.py
│   │   ├── local.py
│   │   └── production.py
│   ├── utils/              # 基礎工具
│   │   ├── env_loader.py
│   │   ├── logger.py
│   │   └── response.py
│   └── apps/
│       └── Calculus_metadata/
│           ├── models/     # 資料模型（4個表格）
│           ├── serializers/ # 數據驗證
│           ├── actors/     # API 處理器
│           ├── services/   # 業務邏輯
│           │   ├── business/   # CRUD 操作
│           │   ├── common/     # 通用工具
│           │   └── optional/   # 計算服務
│           ├── api/        # 路由配置
│           └── tests/      # 測試
├── requirements/           # 依賴管理
├── shell/                  # 管理腳本
├── logs/                   # 日誌
└── docker-compose.yaml     # Docker 配置
```

## 資料庫架構

### SQL Database (PostgreSQL)

1. **students** - 學生資訊
2. **score** - 分數記錄
3. **test** - 考試資訊

### NoSQL Database (MongoDB)

4. **test_pic_information** - 考卷照片與直方圖

## API 端點

### Student_MetadataWriter

- `POST /api/v0.1/Calculus_oom/Calculus_metadata/Student_MetadataWriter/create`
- `POST /api/v0.1/Calculus_oom/Calculus_metadata/Student_MetadataWriter/read`
- `POST /api/v0.1/Calculus_oom/Calculus_metadata/Student_MetadataWriter/update`
- `POST /api/v0.1/Calculus_oom/Calculus_metadata/Student_MetadataWriter/delete`
- `POST /api/v0.1/Calculus_oom/Calculus_metadata/Student_MetadataWriter/status`

### Score_MetadataWriter

- `POST /api/v0.1/Calculus_oom/Calculus_metadata/Score_MetadataWriter/create`
- `POST /api/v0.1/Calculus_oom/Calculus_metadata/Score_MetadataWriter/read`
- `POST /api/v0.1/Calculus_oom/Calculus_metadata/Score_MetadataWriter/update`
- `POST /api/v0.1/Calculus_oom/Calculus_metadata/Score_MetadataWriter/delete`
- `POST /api/v0.1/Calculus_oom/Calculus_metadata/Score_MetadataWriter/calculation_final`
- `POST /api/v0.1/Calculus_oom/Calculus_metadata/Score_MetadataWriter/test_score`

### Test_MetadataWriter

- `POST /api/v0.1/Calculus_oom/Calculus_metadata/Test_MetadataWriter/create`
- `POST /api/v0.1/Calculus_oom/Calculus_metadata/Test_MetadataWriter/read`
- `POST /api/v0.1/Calculus_oom/Calculus_metadata/Test_MetadataWriter/update`
- `POST /api/v0.1/Calculus_oom/Calculus_metadata/Test_MetadataWriter/delete`
- `POST /api/v0.1/Calculus_oom/Calculus_metadata/Test_MetadataWriter/status`
- `POST /api/v0.1/Calculus_oom/Calculus_metadata/Test_MetadataWriter/setweight`

### test-filedata (NonSQL)

- `POST /api/v0.1/Calculus_oom/Calculus_metadata/test-filedata/create`
- `POST /api/v0.1/Calculus_oom/Calculus_metadata/test-filedata/read`
- `POST /api/v0.1/Calculus_oom/Calculus_metadata/test-filedata/update`
- `POST /api/v0.1/Calculus_oom/Calculus_metadata/test-filedata/delete`

## 快速開始

### 1. 環境準備

```bash
# 複製環境變數檔案
cp .env.sample .env

# 編輯 .env 設定資料庫連線資訊
nano .env
```

### 2. 啟動資料庫（Docker）

```bash
# 啟動 PostgreSQL 和 MongoDB
docker-compose up -d postgres mongodb

# 查看容器狀態
docker-compose ps
```

### 3. 安裝依賴

```bash
# 安裝 Python 依賴
pip install -r requirements/local.txt
```

### 4. 資料庫遷移

```bash
# 生成遷移檔案
python manage.py makemigrations

# 執行遷移
python manage.py migrate
```

### 5. 啟動開發伺服器

```bash
# 啟動 Django 開發伺服器
python manage.py runserver 0.0.0.0:8000
```

訪問 http://localhost:8000/admin

## 資料庫測試

執行完整的資料庫連接與 Schema 測試：

```bash
chmod +x setup_and_test.sh
./setup_and_test.sh
```

測試內容：
- PostgreSQL 連接測試
- MongoDB 連接測試
- Django ORM 測試
- Schema 正確性驗證
- CRUD 操作測試

## 資料庫管理界面

### PostgreSQL (pgAdmin)
- URL: http://localhost:5051
- Email: admin@calculus.com
- Password: admin123

### MongoDB (Mongo Express)
- URL: http://localhost:8081
- Username: admin
- Password: admin123

## 開發指南

### 架構規範

本專案嚴格遵守 **Backend Architecture Specification 2.0**：

1. **Request Chain**: `Client → urls.py → Actor → Serializer → Service → Model`
2. **Actor 職責**: HTTP 處理、數據驗證、業務編排、錯誤處理
3. **Service 分層**:
   - Business Service: 通用 CRUD 操作
   - Common Service: UUID、Timestamp、Validation
   - Optional Service: 計算、統計
4. **禁止事項**:
   - ❌ 直接使用 `os.getenv()`（必須透過 env_loader）
   - ❌ 在 Service 中處理 HTTP 請求/響應
   - ❌ 為每個 Model 單獨寫 Service 方法

### 添加新功能

1. **新增 Model**: 在 `models/` 創建新檔案
2. **新增 Serializer**: 在 `serializers/` 創建 Write/Read 兩個
3. **新增 Actor**: 在 `actors/` 創建新的 Actor class
4. **註冊路由**: 在 `api/urls.py` 添加路徑
5. **撰寫測試**: 在 `tests/` 添加測試案例

## 環境變數

| 變數名稱 | 說明 | 預設值 |
|---------|------|--------|
| DJANGO_SECRET_KEY | Django 密鑰 | - |
| DJANGO_DEBUG | 除錯模式 | True |
| DJANGO_ENV | 環境 (local/production) | local |
| DB_HOST | PostgreSQL 主機 | localhost |
| DB_PORT | PostgreSQL 埠號 | 5433 |
| MONGO_HOST | MongoDB 主機 | localhost |
| MONGO_PORT | MongoDB 埠號 | 27017 |

## 測試

```bash
# 執行所有測試
pytest

# 執行特定測試
pytest tests/services/

# 查看測試覆蓋率
pytest --cov=main
```

## 部署

### Docker 部署

```bash
# 建構映像
docker build -t calculus-oom-backend .

# 啟動容器
docker-compose up -d
```

### 生產環境

```bash
# 設定環境變數
export DJANGO_ENV=production

# 使用 gunicorn
gunicorn main.wsgi:application --bind 0.0.0.0:8000
```

## 授權

本專案僅供學術使用。

## 聯絡方式

如有問題請聯絡專案維護者。
