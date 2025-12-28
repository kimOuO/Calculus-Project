"""
Students Model - SQL Database (PostgreSQL)
學生資訊表
"""
from django.db import models


class Students(models.Model):
    """學生資訊 Model"""
    
    # Primary Key
    id = models.AutoField(primary_key=True)
    
    # Business Fields
    student_uuid = models.CharField(
        max_length=255,
        unique=True,
        db_index=True,
        help_text="學生唯一識別碼"
    )
    student_name = models.CharField(
        max_length=255,
        help_text="學生名稱"
    )
    student_number = models.CharField(
        max_length=255,
        unique=True,
        help_text="學生學號"
    )
    student_semester = models.CharField(
        max_length=255,
        help_text="學生學年 (例如: 1141, 1142)"
    )
    
    # Lifecycle Fields
    student_status = models.CharField(
        max_length=255,
        default="修業中",
        help_text="狀態: 修業中/二退/被當/修業完畢"
    )
    student_created_at = models.CharField(
        max_length=255,
        help_text="建立時間"
    )
    student_updated_at = models.CharField(
        max_length=255,
        help_text="更新時間"
    )
    
    class Meta:
        db_table = 'students'
        verbose_name = '學生'
        verbose_name_plural = '學生列表'
        indexes = [
            models.Index(fields=['student_uuid']),
            models.Index(fields=['student_semester']),
            models.Index(fields=['student_status']),
        ]
    
    def __str__(self):
        return f"{self.student_name} ({self.student_number})"
