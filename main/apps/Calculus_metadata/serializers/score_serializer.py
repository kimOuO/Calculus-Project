"""
Score Serializers
"""
from rest_framework import serializers
from main.apps.Calculus_metadata.models import Score


class ScoreWriteSerializer(serializers.Serializer):
    """Score Write Serializer - 用於 Create/Update"""
    
    f_student_uuid = serializers.CharField(
        max_length=255,
        required=True,
        help_text="學生UUID"
    )
    score_quiz1 = serializers.CharField(
        max_length=255,
        required=False,
        allow_blank=True,
        default="",
        help_text="第一次小考分數"
    )
    score_midterm = serializers.CharField(
        max_length=255,
        required=False,
        allow_blank=True,
        default="",
        help_text="期中考分數"
    )
    score_quiz2 = serializers.CharField(
        max_length=255,
        required=False,
        allow_blank=True,
        default="",
        help_text="第二次小考分數"
    )
    score_finalexam = serializers.CharField(
        max_length=255,
        required=False,
        allow_blank=True,
        default="",
        help_text="期末考分數"
    )
    score_total = serializers.CharField(
        max_length=255,
        required=False,
        allow_blank=True,
        default="",
        help_text="總分"
    )


class ScoreReadSerializer(serializers.ModelSerializer):
    """Score Read Serializer - 用於 Read"""
    
    class Meta:
        model = Score
        fields = [
            'id',
            'score_uuid',
            'score_quiz1',
            'score_midterm',
            'score_quiz2',
            'score_finalexam',
            'score_total',
            'f_student_uuid',
            'score_created_at',
            'score_updated_at',
        ]
