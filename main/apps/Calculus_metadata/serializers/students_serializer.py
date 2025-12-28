"""
Students Serializers
"""
from rest_framework import serializers
from main.apps.Calculus_metadata.models import Students


class StudentsWriteSerializer(serializers.Serializer):
    """Students Write Serializer - 用於 Create/Update"""
    
    student_name = serializers.CharField(
        max_length=255,
        required=True,
        help_text="學生名稱"
    )
    student_number = serializers.CharField(
        max_length=255,
        required=True,
        help_text="學生學號"
    )
    student_semester = serializers.CharField(
        max_length=255,
        required=True,
        help_text="學生學年"
    )
    student_status = serializers.CharField(
        max_length=255,
        required=False,
        default="修業中",
        help_text="狀態"
    )
    
    def validate_student_status(self, value):
        """驗證狀態值"""
        allowed_statuses = ["修業中", "二退", "被當", "修業完畢"]
        if value not in allowed_statuses:
            raise serializers.ValidationError(
                f"Invalid status. Must be one of: {', '.join(allowed_statuses)}"
            )
        return value


class StudentsReadSerializer(serializers.ModelSerializer):
    """Students Read Serializer - 用於 Read"""
    
    class Meta:
        model = Students
        fields = [
            'id',
            'student_uuid',
            'student_name',
            'student_number',
            'student_semester',
            'student_status',
            'student_created_at',
            'student_updated_at',
        ]
