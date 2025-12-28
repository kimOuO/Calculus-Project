"""
Test Model - SQL Database (PostgreSQL)
考卷表
"""
from django.db import models


class Test(models.Model):
    """考卷 Model"""
    
    # Primary Key
    id = models.AutoField(primary_key=True)
    
    # Business Fields
    test_uuid = models.CharField(
        max_length=255,
        unique=True,
        db_index=True,
        help_text="考試唯一識別碼"
    )
    test_name = models.CharField(
        max_length=255,
        help_text="考試名稱"
    )
    test_weight = models.CharField(
        max_length=255,
        blank=True,
        default="",
        help_text="權重"
    )
    test_semester = models.CharField(
        max_length=255,
        help_text="學期"
    )
    test_date = models.CharField(
        max_length=255,
        help_text="考試日期"
    )
    test_range = models.CharField(
        max_length=255,
        help_text="考試範圍"
    )
    
    # Cross-database reference to MongoDB
    pt_opt_score_uuid = models.CharField(
        max_length=255,
        blank=True,
        default="",
        help_text="指向 NonSQL database test_pic_information"
    )
    
    # Lifecycle Fields
    test_states = models.CharField(
        max_length=255,
        default="尚未出考卷",
        help_text="狀態: 尚未出考卷/考卷完成/考卷成績結算"
    )
    test_created_at = models.CharField(
        max_length=255,
        help_text="建立時間"
    )
    test_updated_at = models.CharField(
        max_length=255,
        help_text="更新時間"
    )
    
    class Meta:
        db_table = 'test'
        verbose_name = '考卷'
        verbose_name_plural = '考卷列表'
        indexes = [
            models.Index(fields=['test_uuid']),
            models.Index(fields=['test_semester']),
            models.Index(fields=['test_states']),
        ]
    
    def __str__(self):
        return f"{self.test_name} ({self.test_semester})"
