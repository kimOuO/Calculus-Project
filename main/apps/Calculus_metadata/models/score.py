"""
Score Model - SQL Database (PostgreSQL)
分數表
"""
from django.db import models


class Score(models.Model):
    """分數 Model"""
    
    # Primary Key
    id = models.AutoField(primary_key=True)
    
    # Business Fields
    score_uuid = models.CharField(
        max_length=255,
        unique=True,
        db_index=True,
        help_text="分數唯一識別碼"
    )
    score_quiz1 = models.CharField(
        max_length=255,
        blank=True,
        default="",
        help_text="第一次小考分數"
    )
    score_midterm = models.CharField(
        max_length=255,
        blank=True,
        default="",
        help_text="期中考分數"
    )
    score_quiz2 = models.CharField(
        max_length=255,
        blank=True,
        default="",
        help_text="第二次小考分數"
    )
    score_finalexam = models.CharField(
        max_length=255,
        blank=True,
        default="",
        help_text="期末考分數"
    )
    score_total = models.CharField(
        max_length=255,
        blank=True,
        default="",
        help_text="總分"
    )
    
    # Foreign Key (Cross-database reference using CharField)
    f_student_uuid = models.CharField(
        max_length=255,
        db_index=True,
        help_text="外鍵，關聯到 Students.student_uuid"
    )
    
    # Lifecycle Fields (無 status，依據規範)
    score_created_at = models.CharField(
        max_length=255,
        help_text="建立時間"
    )
    score_updated_at = models.CharField(
        max_length=255,
        help_text="更新時間"
    )
    
    class Meta:
        db_table = 'score'
        verbose_name = '分數'
        verbose_name_plural = '分數列表'
        indexes = [
            models.Index(fields=['score_uuid']),
            models.Index(fields=['f_student_uuid']),
        ]
    
    def __str__(self):
        return f"Score {self.score_uuid} (Student: {self.f_student_uuid})"
