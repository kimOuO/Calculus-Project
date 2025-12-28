"""
Timestamp Service - 生成統一格式的時間戳
"""
from datetime import datetime


class TimestampService:
    """時間戳生成服務"""
    
    @staticmethod
    def get_current_timestamp() -> str:
        """
        獲取當前時間戳
        格式: YYYY-MM-DD HH:MM:SS
        
        Returns:
            str: 當前時間戳字串
        """
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    @staticmethod
    def get_current_date() -> str:
        """
        獲取當前日期
        格式: YYYY-MM-DD
        
        Returns:
            str: 當前日期字串
        """
        return datetime.now().strftime("%Y-%m-%d")
    
    @staticmethod
    def get_current_time() -> str:
        """
        獲取當前時間
        格式: HH:MM:SS
        
        Returns:
            str: 當前時間字串
        """
        return datetime.now().strftime("%H:%M:%S")
