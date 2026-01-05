"""
Test Actor - 考試管理
"""
import json
import logging
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.db import transaction

from main.apps.Calculus_metadata.models import Test
from main.apps.Calculus_metadata.serializers import TestWriteSerializer, TestReadSerializer
from main.apps.Calculus_metadata.services.common import UuidService, TimestampService, ValidationService
from main.apps.Calculus_metadata.services.business import SqlDbBusinessService
from main.utils.response import success_response, error_response

logger = logging.getLogger(__name__)


class TestActor:
    """考試 Actor - 處理考試相關的所有業務操作"""
    
    @staticmethod
    @csrf_exempt
    @require_http_methods(["POST"])
    @transaction.atomic
    def create(request):
        """
        創建考試
        POST /api/v0.1/Calculus_oom/Calculus_metadata/Test_MetadataWriter/create
        """
        try:
            # Step 1: 解析請求
            data = json.loads(request.body)
            logger.info(f"Creating test with data: {data}")
            
            # Step 2: 驗證數據
            serializer = TestWriteSerializer(data=data)
            if not serializer.is_valid():
                return error_response("Validation failed", serializer.errors, 400)
            
            validated_data = serializer.validated_data
            
            # Step 3: 生成 UUID 和時間戳
            test_type = "q1"  # 預設，可根據 test_name 推斷
            test_uuid = UuidService.generate_test_uuid(validated_data['test_semester'], test_type)
            timestamp = TimestampService.get_current_timestamp()
            
            # Step 4: 準備完整數據
            complete_data = {
                'test_uuid': test_uuid,
                'test_name': validated_data['test_name'],
                'test_date': validated_data['test_date'],
                'test_range': validated_data['test_range'],
                'test_semester': validated_data['test_semester'],
                'test_weight': validated_data.get('test_weight', ''),
                'test_states': '尚未出考卷',  # 初始狀態
                'pt_opt_score_uuid': '',
                'test_created_at': timestamp,
                'test_updated_at': timestamp,
            }
            
            # Step 5: 創建考試
            test = SqlDbBusinessService.create_entity(Test, complete_data)
            
            # Step 6: 格式化輸出
            output = TestReadSerializer(test).data
            logger.info(f"Test created successfully: {test_uuid}")
            
            return success_response(output, "Test created successfully", 201)
            
        except json.JSONDecodeError:
            return error_response("Invalid JSON format", None, 400)
        except Exception as e:
            logger.error(f"Error creating test: {str(e)}")
            return error_response(f"Unknown error: {str(e)}", None, 500)
    
    @staticmethod
    @csrf_exempt
    @require_http_methods(["POST"])
    def read(request):
        """
        查詢考試
        POST /api/v0.1/Calculus_oom/Calculus_metadata/Test_MetadataWriter/read
        """
        try:
            # Step 1: 解析請求
            data = json.loads(request.body)
            logger.info(f"Reading tests with filters: {data}")
            
            # Step 2: 查詢考試
            if 'test_uuid' in data:
                test = SqlDbBusinessService.get_entity(Test, 'test_uuid', data['test_uuid'])
                if not test:
                    return error_response("Test not found", None, 404)
                output = TestReadSerializer(test).data
            elif data:
                tests = SqlDbBusinessService.get_entities(Test, data)
                output = TestReadSerializer(tests, many=True).data
            else:
                tests = SqlDbBusinessService.get_entities(Test, {})
                output = TestReadSerializer(tests, many=True).data
            
            logger.info(f"Tests retrieved successfully")
            return success_response(output, "Tests retrieved successfully", 200)
            
        except json.JSONDecodeError:
            return error_response("Invalid JSON format", None, 400)
        except Exception as e:
            logger.error(f"Error reading tests: {str(e)}")
            return error_response(f"Unknown error: {str(e)}", None, 500)
    
    @staticmethod
    @csrf_exempt
    @require_http_methods(["POST"])
    @transaction.atomic
    def update(request):
        """
        更新考試
        POST /api/v0.1/Calculus_oom/Calculus_metadata/Test_MetadataWriter/update
        """
        try:
            # Step 1: 解析請求
            data = json.loads(request.body)
            logger.info(f"Updating test with data: {data}")
            
            # Step 2: 驗證必要欄位
            is_valid, missing_keys = ValidationService.validate_required_keys(data, ['test_uuid'])
            if not is_valid:
                return error_response(f"Missing required keys: {missing_keys}", None, 400)
            
            # Step 3: 查詢考試
            test = SqlDbBusinessService.get_entity(Test, 'test_uuid', data['test_uuid'])
            if not test:
                return error_response("Test not found", None, 404)
            
            # Step 4: 驗證更新數據
            update_fields = {k: v for k, v in data.items() if k != 'test_uuid'}
            serializer = TestWriteSerializer(data=update_fields, partial=True)
            if not serializer.is_valid():
                return error_response("Validation failed", serializer.errors, 400)
            
            # Step 5: 更新時間戳
            update_fields['test_updated_at'] = TimestampService.get_current_timestamp()
            
            # Step 6: 執行更新
            updated_test = SqlDbBusinessService.update_entity(test, update_fields)
            
            # Step 7: 格式化輸出
            output = TestReadSerializer(updated_test).data
            logger.info(f"Test updated successfully: {data['test_uuid']}")
            
            return success_response(output, "Test updated successfully", 200)
            
        except json.JSONDecodeError:
            return error_response("Invalid JSON format", None, 400)
        except Exception as e:
            logger.error(f"Error updating test: {str(e)}")
            return error_response(f"Unknown error: {str(e)}", None, 500)
    
    @staticmethod
    @csrf_exempt
    @require_http_methods(["POST"])
    @transaction.atomic
    def delete(request):
        """
        刪除考試
        POST /api/v0.1/Calculus_oom/Calculus_metadata/Test_MetadataWriter/delete
        """
        try:
            # Step 1: 解析請求
            data = json.loads(request.body)
            logger.info(f"Deleting test with data: {data}")
            
            # Step 2: 驗證必要欄位
            is_valid, missing_keys = ValidationService.validate_required_keys(data, ['test_uuid'])
            if not is_valid:
                return error_response(f"Missing required keys: {missing_keys}", None, 400)
            
            # Step 3: 查詢考試
            test = SqlDbBusinessService.get_entity(Test, 'test_uuid', data['test_uuid'])
            if not test:
                return error_response("Test not found", None, 404)
            
            # Step 4: 刪除考試
            SqlDbBusinessService.delete_entity(test)
            
            logger.info(f"Test deleted successfully: {data['test_uuid']}")
            return success_response(None, "Test deleted successfully", 200)
            
        except json.JSONDecodeError:
            return error_response("Invalid JSON format", None, 400)
        except Exception as e:
            logger.error(f"Error deleting test: {str(e)}")
            return error_response(f"Unknown error: {str(e)}", None, 500)
    
    @staticmethod
    @csrf_exempt
    @require_http_methods(["POST"])
    @transaction.atomic
    def status(request):
        """
        更新考試狀態
        POST /api/v0.1/Calculus_oom/Calculus_metadata/Test_MetadataWriter/status
        """
        try:
            # Step 1: 解析請求
            data = json.loads(request.body)
            logger.info(f"Updating test status with data: {data}")
            
            # Step 2: 驗證必要欄位
            is_valid, missing_keys = ValidationService.validate_required_keys(data, ['test_uuid', 'test_state'])
            if not is_valid:
                return error_response(f"Missing required keys: {missing_keys}", None, 400)
            
            # Step 3: 驗證狀態值
            allowed_states = ["尚未出考卷", "考卷完成", "考卷成績結算"]
            if data['test_state'] not in allowed_states:
                return error_response(f"Invalid status. Must be one of: {', '.join(allowed_states)}", None, 400)
            
            # Step 4: 查詢考試
            test = SqlDbBusinessService.get_entity(Test, 'test_uuid', data['test_uuid'])
            if not test:
                return error_response("Test not found", None, 404)
            
            # Step 5: 更新狀態
            update_data = {
                'test_states': data['test_state'],
                'test_updated_at': TimestampService.get_current_timestamp()
            }
            updated_test = SqlDbBusinessService.update_entity(test, update_data)
            
            # Step 6: 格式化輸出
            output = TestReadSerializer(updated_test).data
            logger.info(f"Test status updated successfully: {data['test_uuid']}")
            
            return success_response(output, "Test status updated successfully", 200)
            
        except json.JSONDecodeError:
            return error_response("Invalid JSON format", None, 400)
        except Exception as e:
            logger.error(f"Error updating test status: {str(e)}")
            return error_response(f"Unknown error: {str(e)}", None, 500)
    
    @staticmethod
    @csrf_exempt
    @require_http_methods(["POST"])
    @transaction.atomic
    def setweight(request):
        """
        設定考試權重
        POST /api/v0.1/Calculus_oom/Calculus_metadata/Test_MetadataWriter/setweight
        """
        try:
            # Step 1: 解析請求
            data = json.loads(request.body)
            logger.info(f"Setting test weights with data: {data}")
            
            # Step 2: 驗證必要欄位
            is_valid, missing_keys = ValidationService.validate_required_keys(data, ['test_semester', 'weights'])
            if not is_valid:
                return error_response(f"Missing required keys: {missing_keys}", None, 400)
            
            semester = data['test_semester']
            weights = data['weights']
            
            # Step 3: 驗證權重總和為 1.0
            total_weight = sum(float(w) for w in weights.values())
            if abs(total_weight - 1.0) > 0.001:
                return error_response("Total weight must equal 1.0", None, 400)
            
            # Step 4: 更新每個考試的權重和狀態
            updated_count = 0
            for test_name, weight in weights.items():
                tests = SqlDbBusinessService.get_entities(Test, {
                    'test_semester': semester,
                    'test_name': test_name
                })
                
                for test in tests:
                    update_data = {
                        'test_weight': str(weight),
                        'test_updated_at': TimestampService.get_current_timestamp()
                    }
                    
                    # 只有當狀態為"考卷完成"時，才自動更新為"考卷成績結算"
                    if test.test_states == '考卷完成':
                        update_data['test_states'] = '考卷成績結算'
                        logger.info(f"Auto-updating test status to '考卷成績結算' for test: {test.test_name}")
                    
                    SqlDbBusinessService.update_entity(test, update_data)
                    updated_count += 1
            
            logger.info(f"Test weights set successfully for {updated_count} tests")
            return success_response(
                {'updated_count': updated_count},
                f"Weights set successfully for {updated_count} tests",
                200
            )
            
        except json.JSONDecodeError:
            return error_response("Invalid JSON format", None, 400)
        except Exception as e:
            logger.error(f"Error setting test weights: {str(e)}")
            return error_response(f"Unknown error: {str(e)}", None, 500)
