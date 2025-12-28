"""
Calculation Service - 成績計算相關邏輯
"""
from typing import List, Dict, Any, Optional
import statistics


class CalculationService:
    """計算服務 - 用於成績統計與分析"""
    
    @staticmethod
    def calculate_average(scores: List[float]) -> float:
        """
        計算平均分
        
        Args:
            scores: 分數列表
            
        Returns:
            平均分
        """
        if not scores:
            return 0.0
        return sum(scores) / len(scores)
    
    @staticmethod
    def calculate_median(scores: List[float]) -> float:
        """
        計算中位數
        
        Args:
            scores: 分數列表
            
        Returns:
            中位數
        """
        if not scores:
            return 0.0
        return statistics.median(scores)
    
    @staticmethod
    def calculate_weighted_total(scores: Dict[str, float], weights: Dict[str, float]) -> float:
        """
        計算加權總分
        
        Args:
            scores: 分數字典 {考試名稱: 分數}
            weights: 權重字典 {考試名稱: 權重}
            
        Returns:
            加權總分
        """
        total = 0.0
        for exam_name, score in scores.items():
            if exam_name in weights:
                total += score * weights[exam_name]
        return total
    
    @staticmethod
    def generate_histogram_data(scores: List[float], bin_width: int = 10) -> Dict[str, int]:
        """
        生成直方圖數據（級距分布）
        
        Args:
            scores: 分數列表
            bin_width: 級距寬度（預設 10 分）
            
        Returns:
            級距分布字典 {"0-9": 1, "10-19": 2, ...}
        """
        if not scores:
            return {}
        
        histogram = {}
        min_score = 0
        max_score = 100
        
        # 創建級距
        for start in range(min_score, max_score, bin_width):
            end = start + bin_width - 1
            if end > max_score:
                end = max_score
            bin_key = f"{start}-{end}"
            histogram[bin_key] = 0
        
        # 統計每個級距的數量
        for score in scores:
            bin_index = int(score // bin_width)
            start = bin_index * bin_width
            end = start + bin_width - 1
            if end > max_score:
                end = max_score
            bin_key = f"{start}-{end}"
            if bin_key in histogram:
                histogram[bin_key] += 1
        
        return histogram
    
    @staticmethod
    def filter_valid_scores(scores_dict: Dict[str, str]) -> List[float]:
        """
        過濾並轉換有效分數
        
        Args:
            scores_dict: 分數字典 {欄位名: 分數字串}
            
        Returns:
            有效分數列表（float）
        """
        valid_scores = []
        for score_str in scores_dict.values():
            if score_str and score_str.strip():
                try:
                    score_float = float(score_str)
                    if 0 <= score_float <= 100:
                        valid_scores.append(score_float)
                except ValueError:
                    continue
        return valid_scores
    
    @staticmethod
    def check_passing(total_score: float, passing_threshold: float = 60.0) -> bool:
        """
        檢查是否及格
        
        Args:
            total_score: 總分
            passing_threshold: 及格門檻（預設 60）
            
        Returns:
            是否及格
        """
        return total_score >= passing_threshold
