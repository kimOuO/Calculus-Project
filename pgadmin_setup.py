#!/usr/bin/env python3
"""
pgAdmin 自動註冊 PostgreSQL 服務器腳本
"""
import json
import os
import time
import sys

def create_servers_json():
    """創建servers.json配置文件，自動註冊PostgreSQL服務器"""
    
    servers_config = {
        "Servers": {
            "1": {
                "Name": "Calculus PostgreSQL",
                "Group": "Servers",
                "Host": "calculus_postgres",
                "Port": 5432,
                "MaintenanceDB": "calculus_db",
                "Username": "calculus_user", 
                "Password": "calculus_password123",
                "SSLMode": "prefer",
                "PassFile": "",
                "Comment": "Calculus OOM Database Server"
            }
        }
    }
    
    # 確保目錄存在
    config_dir = "/var/lib/pgadmin/storage/admin_calculus.com"
    os.makedirs(config_dir, exist_ok=True)
    
    # 寫入配置文件
    servers_file = os.path.join(config_dir, "servers.json")
    
    with open(servers_file, 'w') as f:
        json.dump(servers_config, f, indent=2)
    
    print(f"✅ PostgreSQL 服務器配置已創建: {servers_file}")
    return True

def main():
    """主函數"""
    print("🚀 pgAdmin PostgreSQL 自動註冊腳本")
    print("=" * 50)
    
    # 等待pgAdmin完全啟動
    print("⏳ 等待pgAdmin服務啟動...")
    time.sleep(15)
    
    try:
        # 創建服務器配置
        if create_servers_json():
            print("✅ PostgreSQL服務器已自動註冊到pgAdmin")
            print("📋 訪問信息:")
            print("   URL: http://localhost:5051")
            print("   Email: admin@calculus.com")
            print("   Password: admin123")
            print("   服務器: Calculus PostgreSQL (已自動配置)")
        else:
            print("❌ 服務器註冊失敗")
            
    except Exception as e:
        print(f"❌ 錯誤: {str(e)}")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())