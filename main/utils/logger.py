"""
Logger Configuration - 日誌配置
"""
import logging
import os
from datetime import datetime
from pathlib import Path


def setup_logger(name: str = 'calculus_oom', log_dir: str = 'logs', level=logging.INFO):
    """
    配置日誌記錄器
    
    Args:
        name: Logger 名稱
        log_dir: 日誌目錄
        level: 日誌級別
        
    Returns:
        Logger 實例
    """
    # 創建日誌目錄
    log_path = Path(log_dir)
    log_path.mkdir(parents=True, exist_ok=True)
    
    # 生成日誌檔案名稱（按日期分檔）
    today = datetime.now().strftime('%Y-%m-%d')
    log_file = log_path / f'{name}_{today}.log'
    
    # 創建 logger
    logger = logging.getLogger(name)
    logger.setLevel(level)
    
    # 避免重複添加 handler
    if logger.handlers:
        return logger
    
    # 創建檔案 handler
    file_handler = logging.FileHandler(log_file, encoding='utf-8')
    file_handler.setLevel(level)
    
    # 創建控制台 handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(level)
    
    # 創建格式化器
    formatter = logging.Formatter(
        '[%(asctime)s] %(levelname)s [%(name)s.%(funcName)s:%(lineno)d] %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)
    
    # 添加 handler
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    return logger


def get_logger(name: str = 'calculus_oom'):
    """
    獲取 Logger 實例
    
    Args:
        name: Logger 名稱
        
    Returns:
        Logger 實例
    """
    return logging.getLogger(name)
