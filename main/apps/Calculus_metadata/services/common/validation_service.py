"""
Validation Service - 通用數據驗證工具
"""
from typing import Dict, Any, List


class ValidationService:
    """數據驗證服務"""
    
    @staticmethod
    def validate_required_keys(data: Dict[str, Any], required_keys: List[str]) -> tuple:
        """
        驗證必要欄位是否存在
        
        Args:
            data: 待驗證的數據字典
            required_keys: 必要欄位列表
            
        Returns:
            tuple: (is_valid, missing_keys)
        """
        missing_keys = [key for key in required_keys if key not in data or data[key] is None]
        return len(missing_keys) == 0, missing_keys
    
    @staticmethod
    def validate_status_transition(current_status: str, new_status: str, allowed_transitions: Dict[str, List[str]]) -> bool:
        """
        驗證狀態轉換是否合法
        
        Args:
            current_status: 當前狀態
            new_status: 新狀態
            allowed_transitions: 允許的狀態轉換字典
            
        Returns:
            bool: 是否允許轉換
        """
        if current_status not in allowed_transitions:
            return False
        return new_status in allowed_transitions[current_status]
    
    @staticmethod
    def validate_score_value(score: str) -> tuple:
        """
        驗證分數值是否合法
        
        Args:
            score: 分數字串
            
        Returns:
            tuple: (is_valid, error_message)
        """
        if not score or score == "":
            return True, None  # 空值允許
        
        try:
            score_float = float(score)
            if 0 <= score_float <= 100:
                return True, None
            else:
                return False, "Score must be between 0 and 100"
        except ValueError:
            return False, "Score must be a valid number"
    
    @staticmethod
    def validate_semester_format(semester: str) -> tuple:
        """
        驗證學期格式
        格式: 4位數字 (例如: 1141, 1142)
        
        Args:
            semester: 學期字串
            
        Returns:
            tuple: (is_valid, error_message)
        """
        if len(semester) != 4:
            return False, "Semester must be 4 digits"
        
        if not semester.isdigit():
            return False, "Semester must contain only digits"
        
        return True, None
