"""
SQL Database Operations - 通用 CRUD 服務
"""
from typing import Type, Dict, Any, List, Optional
from django.db import models
from django.core.exceptions import ObjectDoesNotExist


class SqlDbBusinessService:
    """SQL 資料庫通用業務服務"""
    
    @staticmethod
    def create_entity(model_class: Type[models.Model], validated_data: Dict[str, Any]) -> models.Model:
        """
        通用創建實體方法
        
        Args:
            model_class: Model 類別
            validated_data: 已驗證的數據
            
        Returns:
            創建的實體實例
        """
        return model_class.objects.create(**validated_data)
    
    @staticmethod
    def get_entity(model_class: Type[models.Model], uuid_field: str, uuid_value: str) -> Optional[models.Model]:
        """
        通用查詢單個實體方法
        
        Args:
            model_class: Model 類別
            uuid_field: UUID 欄位名稱
            uuid_value: UUID 值
            
        Returns:
            查詢到的實體實例或 None
        """
        try:
            return model_class.objects.get(**{uuid_field: uuid_value})
        except ObjectDoesNotExist:
            return None
    
    @staticmethod
    def get_entities(model_class: Type[models.Model], filters: Dict[str, Any]) -> List[models.Model]:
        """
        通用查詢多個實體方法
        
        Args:
            model_class: Model 類別
            filters: 過濾條件字典
            
        Returns:
            實體列表
        """
        if not filters:
            return list(model_class.objects.all())
        return list(model_class.objects.filter(**filters))
    
    @staticmethod
    def update_entity(entity: models.Model, update_data: Dict[str, Any]) -> models.Model:
        """
        通用更新實體方法
        
        Args:
            entity: 待更新的實體實例
            update_data: 更新數據字典
            
        Returns:
            更新後的實體實例
        """
        for key, value in update_data.items():
            setattr(entity, key, value)
        entity.save()
        return entity
    
    @staticmethod
    def delete_entity(entity: models.Model) -> None:
        """
        通用刪除實體方法
        
        Args:
            entity: 待刪除的實體實例
        """
        entity.delete()
    
    @staticmethod
    def delete_entities(model_class: Type[models.Model], filters: Dict[str, Any]) -> int:
        """
        通用批量刪除實體方法
        
        Args:
            model_class: Model 類別
            filters: 過濾條件字典
            
        Returns:
            刪除的實體數量
        """
        queryset = model_class.objects.filter(**filters)
        count = queryset.count()
        queryset.delete()
        return count
    
    @staticmethod
    def entity_exists(model_class: Type[models.Model], uuid_field: str, uuid_value: str) -> bool:
        """
        檢查實體是否存在
        
        Args:
            model_class: Model 類別
            uuid_field: UUID 欄位名稱
            uuid_value: UUID 值
            
        Returns:
            是否存在
        """
        return model_class.objects.filter(**{uuid_field: uuid_value}).exists()
    
    @staticmethod
    def count_entities(model_class: Type[models.Model], filters: Dict[str, Any]) -> int:
        """
        計算實體數量
        
        Args:
            model_class: Model 類別
            filters: 過濾條件字典
            
        Returns:
            實體數量
        """
        return model_class.objects.filter(**filters).count()
