#!/bin/bash

# Calculus OOM Backend - 專案初始化腳本

echo "========================================="
echo "Calculus OOM Backend - 專案初始化"
echo "========================================="

# 檢查 Python 環境
echo "檢查 Python 版本..."
python3 --version

# 安裝依賴
echo "安裝 Python 依賴..."
pip install -r requirements/local.txt

# 建立必要目錄
echo "建立必要目錄..."
mkdir -p logs uploads staticfiles media

# 環境變數檢查
if [ ! -f .env ]; then
    echo "複製 .env.sample 到 .env..."
    cp .env.sample .env
    echo "請編輯 .env 檔案設定環境變數"
fi

# 資料庫遷移
echo "執行資料庫遷移..."
python manage.py makemigrations
python manage.py migrate

# 建立超級使用者（可選）
echo "是否要建立 Django 超級使用者？(y/n)"
read -r create_superuser
if [ "$create_superuser" = "y" ]; then
    python manage.py createsuperuser
fi

echo "========================================="
echo "初始化完成！"
echo "執行以下命令啟動開發伺服器："
echo "python manage.py runserver 0.0.0.0:8000"
echo "========================================="
