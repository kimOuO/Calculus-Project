"""
TestPicInformation Serializers
"""
from rest_framework import serializers


class TestPicInformationWriteSerializer(serializers.Serializer):
    """TestPicInformation Write Serializer - 用於 Create/Update"""
    
    test_pic = serializers.CharField(
        max_length=255,
        required=False,
        allow_blank=True,
        default="",
        help_text="考卷照片路徑"
    )
    test_pic_histogram = serializers.CharField(
        max_length=255,
        required=False,
        allow_blank=True,
        default="",
        help_text="直方圖路徑"
    )


class TestPicInformationReadSerializer(serializers.Serializer):
    """TestPicInformation Read Serializer - 用於 Read"""
    
    test_pic_uuid = serializers.CharField()
    test_pic = serializers.CharField()
    test_pic_histogram = serializers.CharField()
    pic_created_at = serializers.CharField()
    pic_updated_at = serializers.CharField()
