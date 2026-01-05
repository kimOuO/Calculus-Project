"""
Environment Loader - 環境變數載入器
"""
import os
from pathlib import Path
from dotenv import load_dotenv

# 自動加載 .env 文件
BASE_DIR = Path(__file__).resolve().parent.parent.parent
load_dotenv(dotenv_path=BASE_DIR / '.env')


def get_env(key: str, default: str = None) -> str:
    """
    獲取環境變數
    
    Args:
        key: 環境變數名稱
        default: 預設值
        
    Returns:
        環境變數值
    """
    return os.environ.get(key, default)


def get_env_bool(key: str, default: bool = False) -> bool:
    """
    獲取布林類型環境變數
    
    Args:
        key: 環境變數名稱
        default: 預設值
        
    Returns:
        布林值
    """
    value = get_env(key, str(default))
    return value.lower() in ('true', '1', 'yes', 'on')


def get_env_int(key: str, default: int = 0) -> int:
    """
    獲取整數類型環境變數
    
    Args:
        key: 環境變數名稱
        default: 預設值
        
    Returns:
        整數值
    """
    try:
        return int(get_env(key, str(default)))
    except ValueError:
        return default


def get_env_list(key: str, default: list = None, separator: str = ',') -> list:
    """
    獲取列表類型環境變數
    
    Args:
        key: 環境變數名稱
        default: 預設值
        separator: 分隔符
        
    Returns:
        列表
    """
    if default is None:
        default = []
    
    value = get_env(key)
    if value:
        return [item.strip() for item in value.split(separator)]
    return default


def load_env_from_file(env_file: str = '.env'):
    """
    從檔案載入環境變數
    
    Args:
        env_file: .env 檔案路徑
    """
    env_path = Path(env_file)
    if env_path.exists():
        with open(env_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    key = key.strip()
                    value = value.strip().strip('"').strip("'")
                    os.environ.setdefault(key, value)
