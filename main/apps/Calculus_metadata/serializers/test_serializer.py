"""
Test Serializers
"""
from rest_framework import serializers
from main.apps.Calculus_metadata.models import Test


class TestWriteSerializer(serializers.Serializer):
    """Test Write Serializer - 用於 Create/Update"""
    
    test_name = serializers.CharField(
        max_length=255,
        required=True,
        help_text="考試名稱"
    )
    test_date = serializers.CharField(
        max_length=255,
        required=True,
        help_text="考試日期"
    )
    test_range = serializers.CharField(
        max_length=255,
        required=True,
        help_text="考試範圍"
    )
    test_semester = serializers.CharField(
        max_length=255,
        required=True,
        help_text="學期"
    )
    test_weight = serializers.CharField(
        max_length=255,
        required=False,
        allow_blank=True,
        default="",
        help_text="權重"
    )
    test_states = serializers.CharField(
        max_length=255,
        required=False,
        default="尚未出考卷",
        help_text="狀態"
    )
    pt_opt_score_uuid = serializers.CharField(
        max_length=255,
        required=False,
        allow_blank=True,
        default="",
        help_text="NonSQL 資料庫 UUID"
    )
    
    def validate_test_states(self, value):
        """驗證狀態值"""
        allowed_states = ["尚未出考卷", "考卷完成", "考卷成績結算"]
        if value not in allowed_states:
            raise serializers.ValidationError(
                f"Invalid state. Must be one of: {', '.join(allowed_states)}"
            )
        return value


class TestReadSerializer(serializers.ModelSerializer):
    """Test Read Serializer - 用於 Read"""
    
    class Meta:
        model = Test
        fields = [
            'id',
            'test_uuid',
            'test_name',
            'test_weight',
            'test_semester',
            'test_date',
            'test_range',
            'pt_opt_score_uuid',
            'test_states',
            'test_created_at',
            'test_updated_at',
        ]
