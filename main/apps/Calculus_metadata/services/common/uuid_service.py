"""
UUID Service - 生成統一格式的 UUID
"""
import uuid
from datetime import datetime


class UuidService:
    """UUID 生成服務"""
    
    @staticmethod
    def generate_student_uuid(semester: str) -> str:
        """
        生成學生 UUID
        格式: stu_{semester}_{sequence}_{random}
        
        Args:
            semester: 學期 (例如: 1141, 1142)
            
        Returns:
            str: 生成的 UUID
        """
        random_suffix = str(uuid.uuid4())[:8]
        timestamp_suffix = datetime.now().strftime("%m%d")
        return f"stu_{semester}_{timestamp_suffix}_{random_suffix}"
    
    @staticmethod
    def generate_score_uuid(semester: str) -> str:
        """
        生成分數 UUID
        格式: scr_{semester}_{sequence}_{random}
        
        Args:
            semester: 學期
            
        Returns:
            str: 生成的 UUID
        """
        random_suffix = str(uuid.uuid4())[:8]
        timestamp_suffix = datetime.now().strftime("%m%d")
        return f"scr_{semester}_{timestamp_suffix}_{random_suffix}"
    
    @staticmethod
    def generate_test_uuid(semester: str, test_type: str = "q1") -> str:
        """
        生成考試 UUID
        格式: tst_{semester}_{test_type}_{random}
        
        Args:
            semester: 學期
            test_type: 考試類型 (q1, mid, q2, final)
            
        Returns:
            str: 生成的 UUID
        """
        random_suffix = str(uuid.uuid4())[:8]
        return f"tst_{semester}_{test_type}_{random_suffix}"
    
    @staticmethod
    def generate_test_pic_uuid(semester: str, test_type: str = "q1") -> str:
        """
        生成考卷照片 UUID
        格式: tpic_{semester}_{test_type}_{random}
        
        Args:
            semester: 學期
            test_type: 考試類型
            
        Returns:
            str: 生成的 UUID
        """
        random_suffix = str(uuid.uuid4())[:8]
        return f"tpic_{semester}_{test_type}_{random_suffix}"
    
    @staticmethod
    def generate_generic_uuid(prefix: str = "gen") -> str:
        """
        生成通用 UUID
        
        Args:
            prefix: UUID 前綴
            
        Returns:
            str: 生成的 UUID
        """
        random_suffix = str(uuid.uuid4())[:8]
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        return f"{prefix}_{timestamp}_{random_suffix}"
