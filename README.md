# Calculus OOM Backend

> 微積分課程成績管理系統後端 - 基於 Django 的 RESTful API 服務

## 🎯 專案概述

這是一個專為微積分課程設計的成績管理系統後端，提供完整的學生資料管理、考試安排、成績錄入計算及檔案管理功能。系統採用 Django 框架，使用 PostgreSQL 作為主要資料庫，MongoDB 作為檔案儲存，支援 Docker 容器化部署。

## 📋 核心功能

| 模組 | 功能描述 | API 數量 | 主要特色 |
|------|----------|----------|----------|
| **學生管理** | 學生資料 CRUD、狀態管理、Excel 批量操作 | 7 個 | 支援學生狀態流轉、批量匯入匯出 |
| **考試管理** | 考試規劃、權重設定、狀態追蹤 | 6 個 | 自動權重驗證、狀態自動更新 |
| **成績管理** | 成績錄入、總分計算、統計分析 | 6 個 | 加權平均計算、視覺化分析 |
| **檔案管理** | 考卷上傳、圖片儲存、檔案檢視 | 4 個 | 多檔案上傳、MongoDB 儲存 |

### 🔗 API 端點總覽

| 類型 | 端點 | 方法 | 功能 |
|------|------|------|------|
| 學生 | `/Student_MetadataWriter/create` | POST | 建立學生 |
| 學生 | `/Student_MetadataWriter/upload_excel` | POST | Excel 批量匯入 |
| 學生 | `/Student_MetadataWriter/read` | POST | 查詢學生資料 |
| 學生 | `/Student_MetadataWriter/update` | POST | 更新學生資訊 |
| 學生 | `/Student_MetadataWriter/delete` | POST | 刪除學生 |
| 學生 | `/Student_MetadataWriter/status` | POST | 更新學生狀態 |
| 學生 | `/Student_MetadataWriter/feedback_excel` | POST | 匯出成績報表 |
| 成績 | `/Score_MetadataWriter/create` | POST | 錄入成績 |
| 成績 | `/Score_MetadataWriter/read` | POST | 查詢成績 |
| 成績 | `/Score_MetadataWriter/update` | POST | 更新成績 |
| 成績 | `/Score_MetadataWriter/delete` | POST | 刪除成績 |
| 成績 | `/Score_MetadataWriter/calculation_final` | POST | 計算總成績 |
| 成績 | `/Score_MetadataWriter/test_score` | POST | 成績統計分析 |
| 成績 | `/Score_MetadataWriter/step_diagram` | POST | 生成分布圖 |
| 考試 | `/Test_MetadataWriter/create` | POST | 建立考試 |
| 考試 | `/Test_MetadataWriter/read` | POST | 查詢考試資料 |
| 考試 | `/Test_MetadataWriter/update` | POST | 更新考試資訊 |
| 考試 | `/Test_MetadataWriter/delete` | POST | 刪除考試 |
| 考試 | `/Test_MetadataWriter/status` | POST | 更新考試狀態 |
| 考試 | `/Test_MetadataWriter/setweight` | POST | 設定考試權重 |
| 檔案 | `/test-filedata/create` | POST | 上傳檔案 |
| 檔案 | `/test-filedata/read` | POST | 讀取檔案 |
| 檔案 | `/test-filedata/update` | POST | 更新檔案 |
| 檔案 | `/test-filedata/delete` | POST | 刪除檔案 |

**API Base URL**: `http://localhost:8000/api/v0.1/Calculus_oom/Calculus_metadata`

## 🐳 Docker 環境要求

| 服務 | 版本 | 用途 |
|------|------|------|
| **Docker** | 29.2.1+ | 容器運行環境 |
| **Docker Compose** | 1.29.2+ | 服務編排 |
| **PostgreSQL** | 15-alpine | 主要資料庫 |
| **MongoDB** | 7.0 | 檔案儲存 |
| **pgAdmin** | latest | 資料庫管理介面 |
| **Python** | 3.11-slim | 應用運行環境 |

## 📦 系統需求

### 基本需求
- **作業系統**: Linux (Ubuntu 20.04+ 推薦)
- **記憶體**: 4GB+ 
- **硬碟空間**: 10GB+
- **網路**: 網際網路連接（初次安裝需下載 Docker 映像）

### 軟體依賴
- Git
- Docker & Docker Compose
- Bash shell

## 🚀 快速啟動指南

### 1. 取得專案
```bash
git clone https://github.com/kimOuO/Calculus-Project.git
cd Calculus-Project
```

### 2. 一鍵部署
```bash
chmod +x deploy.sh
./deploy.sh
```

### 3. 驗證部署
部署完成後，系統將提供以下服務：

| 服務 | 訪問地址 | 說明 |
|------|----------|------|
| **Django API** | http://localhost:8000 | 主要 API 服務 |
| **pgAdmin** | http://localhost:5051 | 資料庫管理 |
| **PostgreSQL** | localhost:5433 | 資料庫連接 |
| **MongoDB** | localhost:27017 | 檔案儲存 |

### 4. 測試 API
```bash
python3 test_api.py
```

## 🏗️ 系統架構圖

```
┌─────────────────────────────────────────────────────┐
│                   Frontend                          │
│              (React/Vue/Angular)                    │
└─────────────────────┬───────────────────────────────┘
                      │ HTTP/REST API
                      │
┌─────────────────────▼───────────────────────────────┐
│                Django Backend                       │
│  ┌─────────────┬─────────────┬─────────────────────┐│
│  │   Student   │    Test     │       Score         ││
│  │   Actor     │   Actor     │       Actor         ││
│  └─────────────┴─────────────┴─────────────────────┘│
│  ┌─────────────────────────────────────────────────┐│
│  │            TestFiledata Actor                   ││
│  └─────────────────────────────────────────────────┘│
└─────────────┬───────────────────────┬───────────────┘
              │                       │
              ▼                       ▼
┌─────────────────────────┐ ┌─────────────────────────┐
│      PostgreSQL         │ │       MongoDB           │
│   (Structured Data)     │ │   (File Storage)        │
│                         │ │                         │
│ • Students              │ │ • Exam Papers           │
│ • Tests                 │ │ • Histograms            │ 
│ • Scores                │ │ • Images                │
└─────────────────────────┘ └─────────────────────────┘

┌─────────────────────────────────────────────────────┐
│                  pgAdmin                            │
│               (DB Management)                       │
└─────────────────────────────────────────────────────┘
```

### 資料流程圖
```
學生註冊 → 考試規劃 → 權重設定 → 考卷上傳 → 成績錄入 → 總分計算 → 統計分析
    │         │         │         │         │         │         │
    ▼         ▼         ▼         ▼         ▼         ▼         ▼
PostgreSQL PostgreSQL PostgreSQL MongoDB PostgreSQL PostgreSQL MongoDB
(Students) (Tests)   (Tests)   (Files)  (Scores)  (Scores)  (Charts)
```

## 🛠️ 管理指令

### 服務管理
```bash
# 查看服務狀態
sudo docker ps

# 查看後端日誌
sudo docker logs -f calculus_backend

# 重啟服務
sudo docker restart calculus_backend

# 停止所有服務
sudo docker-compose down && sudo docker stop calculus_backend
```

### 資料庫管理
```bash
# 進入 PostgreSQL 容器
sudo docker exec -it calculus_postgres psql -U calculus_user -d calculus_db

# 進入 MongoDB 容器
sudo docker exec -it calculus_mongodb mongosh
```

## 📧 pgAdmin 登入資訊
- **URL**: http://localhost:5051
- **Email**: admin@calculus.com  
- **Password**: admin123
- **PostgreSQL 伺服器**: 已自動註冊為 "Calculus PostgreSQL"

## 🔧 開發相關

### API 測試
- **測試腳本**: `python3 test_api.py`
- **測試覆蓋率**: 100% (14/14 個 API 通過)
- **測試範圍**: CRUD 操作、業務邏輯、錯誤處理

### 專案結構
```
Calculus-Project/
├── main/                      # Django 主應用
│   ├── apps/Calculus_metadata/   # 核心業務邏輯
│   │   ├── actors/               # API 處理層
│   │   ├── models/               # 資料模型
│   │   ├── serializers/          # 序列化器
│   │   └── services/             # 業務服務
│   └── settings/                 # Django 設定
├── deploy.sh                   # 一鍵部署腳本
├── docker-compose.yaml         # 服務編排
├── Dockerfile                  # 容器定義
├── docker-entrypoint.sh        # 容器入口點
├── test_api.py                 # API 測試腳本
└── requirements/               # Python 依賴
```

## 📝 授權

本專案採用 MIT 授權條款。

---

**🚀 立即開始使用 `./deploy.sh` 一鍵部署！**