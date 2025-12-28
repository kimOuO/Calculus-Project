"""
Students Actor - 學生資料管理
"""
import json
import logging
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.db import transaction

from main.apps.Calculus_metadata.models import Students, Score
from main.apps.Calculus_metadata.serializers import StudentsWriteSerializer, StudentsReadSerializer
from main.apps.Calculus_metadata.services.common import UuidService, TimestampService, ValidationService
from main.apps.Calculus_metadata.services.business import SqlDbBusinessService
from main.utils.response import success_response, error_response

logger = logging.getLogger(__name__)


class StudentActor:
    """學生資料 Actor - 處理學生相關的所有業務操作"""
    
    @staticmethod
    @csrf_exempt
    @require_http_methods(["POST"])
    @transaction.atomic
    def create(request):
        """
        創建學生
        POST /api/v0.1/Calculus_oom/Calculus_metadata/Student_MetadataWriter/create
        """
        try:
            # Step 1: 解析請求
            data = json.loads(request.body)
            logger.info(f"Creating student with data: {data}")
            
            # Step 2: 驗證數據
            serializer = StudentsWriteSerializer(data=data)
            if not serializer.is_valid():
                return error_response("Validation failed", serializer.errors, 400)
            
            validated_data = serializer.validated_data
            
            # Step 3: 生成 UUID 和時間戳
            student_uuid = UuidService.generate_student_uuid(validated_data['student_semester'])
            timestamp = TimestampService.get_current_timestamp()
            
            # Step 4: 準備完整數據
            complete_data = {
                'student_uuid': student_uuid,
                'student_name': validated_data['student_name'],
                'student_number': validated_data['student_number'],
                'student_semester': validated_data['student_semester'],
                'student_status': validated_data.get('student_status', '修業中'),
                'student_created_at': timestamp,
                'student_updated_at': timestamp,
            }
            
            # Step 5: 創建學生（通過 Business Service）
            student = SqlDbBusinessService.create_entity(Students, complete_data)
            
            # Step 6: 同時創建對應的成績記錄
            score_uuid = UuidService.generate_score_uuid(validated_data['student_semester'])
            score_data = {
                'score_uuid': score_uuid,
                'f_student_uuid': student_uuid,
                'score_quiz1': '',
                'score_midterm': '',
                'score_quiz2': '',
                'score_finalexam': '',
                'score_total': '',
                'score_created_at': timestamp,
                'score_updated_at': timestamp,
            }
            SqlDbBusinessService.create_entity(Score, score_data)
            
            # Step 7: 格式化輸出
            output = StudentsReadSerializer(student).data
            logger.info(f"Student created successfully: {student_uuid}")
            
            return success_response(output, "Student created successfully", 201)
            
        except json.JSONDecodeError:
            return error_response("Invalid JSON format", None, 400)
        except Exception as e:
            logger.error(f"Error creating student: {str(e)}")
            return error_response(f"Unknown error: {str(e)}", None, 500)
    
    @staticmethod
    @csrf_exempt
    @require_http_methods(["POST"])
    def read(request):
        """
        查詢學生
        POST /api/v0.1/Calculus_oom/Calculus_metadata/Student_MetadataWriter/read
        """
        try:
            # Step 1: 解析請求
            data = json.loads(request.body)
            logger.info(f"Reading students with filters: {data}")
            
            # Step 2: 判斷查詢類型
            if 'student_uuid' in data:
                # 單個查詢
                student = SqlDbBusinessService.get_entity(Students, 'student_uuid', data['student_uuid'])
                if not student:
                    return error_response("Student not found", None, 404)
                output = StudentsReadSerializer(student).data
            elif data:
                # 條件查詢
                students = SqlDbBusinessService.get_entities(Students, data)
                output = StudentsReadSerializer(students, many=True).data
            else:
                # 查詢全部
                students = SqlDbBusinessService.get_entities(Students, {})
                output = StudentsReadSerializer(students, many=True).data
            
            logger.info(f"Students retrieved successfully")
            return success_response(output, "Students retrieved successfully", 200)
            
        except json.JSONDecodeError:
            return error_response("Invalid JSON format", None, 400)
        except Exception as e:
            logger.error(f"Error reading students: {str(e)}")
            return error_response(f"Unknown error: {str(e)}", None, 500)
    
    @staticmethod
    @csrf_exempt
    @require_http_methods(["POST"])
    @transaction.atomic
    def update(request):
        """
        更新學生
        POST /api/v0.1/Calculus_oom/Calculus_metadata/Student_MetadataWriter/update
        """
        try:
            # Step 1: 解析請求
            data = json.loads(request.body)
            logger.info(f"Updating student with data: {data}")
            
            # Step 2: 驗證必要欄位
            is_valid, missing_keys = ValidationService.validate_required_keys(data, ['student_uuid'])
            if not is_valid:
                return error_response(f"Missing required keys: {missing_keys}", None, 400)
            
            # Step 3: 查詢學生
            student = SqlDbBusinessService.get_entity(Students, 'student_uuid', data['student_uuid'])
            if not student:
                return error_response("Student not found", None, 404)
            
            # Step 4: 驗證更新數據
            update_fields = {k: v for k, v in data.items() if k != 'student_uuid'}
            serializer = StudentsWriteSerializer(data=update_fields, partial=True)
            if not serializer.is_valid():
                return error_response("Validation failed", serializer.errors, 400)
            
            # Step 5: 更新時間戳
            update_fields['student_updated_at'] = TimestampService.get_current_timestamp()
            
            # Step 6: 執行更新
            updated_student = SqlDbBusinessService.update_entity(student, update_fields)
            
            # Step 7: 格式化輸出
            output = StudentsReadSerializer(updated_student).data
            logger.info(f"Student updated successfully: {data['student_uuid']}")
            
            return success_response(output, "Student updated successfully", 200)
            
        except json.JSONDecodeError:
            return error_response("Invalid JSON format", None, 400)
        except Exception as e:
            logger.error(f"Error updating student: {str(e)}")
            return error_response(f"Unknown error: {str(e)}", None, 500)
    
    @staticmethod
    @csrf_exempt
    @require_http_methods(["POST"])
    @transaction.atomic
    def delete(request):
        """
        刪除學生（級聯刪除相關成績）
        POST /api/v0.1/Calculus_oom/Calculus_metadata/Student_MetadataWriter/delete
        """
        try:
            # Step 1: 解析請求
            data = json.loads(request.body)
            logger.info(f"Deleting student with data: {data}")
            
            # Step 2: 驗證必要欄位
            is_valid, missing_keys = ValidationService.validate_required_keys(data, ['student_uuid'])
            if not is_valid:
                return error_response(f"Missing required keys: {missing_keys}", None, 400)
            
            # Step 3: 查詢學生
            student = SqlDbBusinessService.get_entity(Students, 'student_uuid', data['student_uuid'])
            if not student:
                return error_response("Student not found", None, 404)
            
            # Step 4: 刪除相關成績（級聯刪除）
            deleted_scores = SqlDbBusinessService.delete_entities(Score, {'f_student_uuid': data['student_uuid']})
            logger.info(f"Deleted {deleted_scores} related scores")
            
            # Step 5: 刪除學生
            SqlDbBusinessService.delete_entity(student)
            
            logger.info(f"Student deleted successfully: {data['student_uuid']}")
            return success_response(None, "Student and related scores deleted successfully", 200)
            
        except json.JSONDecodeError:
            return error_response("Invalid JSON format", None, 400)
        except Exception as e:
            logger.error(f"Error deleting student: {str(e)}")
            return error_response(f"Unknown error: {str(e)}", None, 500)
    
    @staticmethod
    @csrf_exempt
    @require_http_methods(["POST"])
    @transaction.atomic
    def status(request):
        """
        更新學生狀態
        POST /api/v0.1/Calculus_oom/Calculus_metadata/Student_MetadataWriter/status
        """
        try:
            # Step 1: 解析請求
            data = json.loads(request.body)
            logger.info(f"Updating student status with data: {data}")
            
            # Step 2: 驗證必要欄位
            is_valid, missing_keys = ValidationService.validate_required_keys(data, ['student_uuid', 'student_status'])
            if not is_valid:
                return error_response(f"Missing required keys: {missing_keys}", None, 400)
            
            # Step 3: 驗證狀態值
            allowed_statuses = ["修業中", "二退", "被當", "修業完畢"]
            if data['student_status'] not in allowed_statuses:
                return error_response(f"Invalid status. Must be one of: {', '.join(allowed_statuses)}", None, 400)
            
            # Step 4: 查詢學生
            student = SqlDbBusinessService.get_entity(Students, 'student_uuid', data['student_uuid'])
            if not student:
                return error_response("Student not found", None, 404)
            
            # Step 5: 更新狀態
            update_data = {
                'student_status': data['student_status'],
                'student_updated_at': TimestampService.get_current_timestamp()
            }
            
            # Step 6: 如果狀態改為「二退」，清空該學生的所有成績
            if data['student_status'] == '二退':
                scores = SqlDbBusinessService.get_entities(Score, {'f_student_uuid': data['student_uuid']})
                for score in scores:
                    clear_data = {
                        'score_quiz1': '',
                        'score_midterm': '',
                        'score_quiz2': '',
                        'score_finalexam': '',
                        'score_total': '',
                        'score_updated_at': TimestampService.get_current_timestamp()
                    }
                    SqlDbBusinessService.update_entity(score, clear_data)
                logger.info(f"Cleared scores for student: {data['student_uuid']}")
            
            updated_student = SqlDbBusinessService.update_entity(student, update_data)
            
            # Step 7: 格式化輸出
            output = StudentsReadSerializer(updated_student).data
            logger.info(f"Student status updated successfully: {data['student_uuid']}")
            
            return success_response(output, "Student status updated successfully", 200)
            
        except json.JSONDecodeError:
            return error_response("Invalid JSON format", None, 400)
        except Exception as e:
            logger.error(f"Error updating student status: {str(e)}")
            return error_response(f"Unknown error: {str(e)}", None, 500)
