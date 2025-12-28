"""
Score Actor - 分數管理
"""
import json
import logging
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.db import transaction

from main.apps.Calculus_metadata.models import Score, Students, Test
from main.apps.Calculus_metadata.serializers import ScoreWriteSerializer, ScoreReadSerializer
from main.apps.Calculus_metadata.services.common import UuidService, TimestampService, ValidationService
from main.apps.Calculus_metadata.services.business import SqlDbBusinessService
from main.apps.Calculus_metadata.services.optional.calculation import CalculationService
from main.utils.response import success_response, error_response

logger = logging.getLogger(__name__)


class ScoreActor:
    """分數 Actor - 處理分數相關的所有業務操作"""
    
    @staticmethod
    @csrf_exempt
    @require_http_methods(["POST"])
    @transaction.atomic
    def create(request):
        """
        創建/更新分數
        POST /api/v0.1/Calculus_oom/Calculus_metadata/Score_MetadataWriter/create
        """
        try:
            # Step 1: 解析請求
            data = json.loads(request.body)
            logger.info(f"Creating/Updating score with data: {data}")
            
            # Step 2: 驗證必要欄位
            is_valid, missing_keys = ValidationService.validate_required_keys(
                data, ['f_student_uuid', 'update_field', 'score_value']
            )
            if not is_valid:
                return error_response(f"Missing required keys: {missing_keys}", None, 400)
            
            # Step 3: 驗證學生是否存在
            student = SqlDbBusinessService.get_entity(Students, 'student_uuid', data['f_student_uuid'])
            if not student:
                return error_response("Student not found", None, 404)
            
            # Step 4: 驗證分數欄位
            allowed_fields = ['score_quiz1', 'score_midterm', 'score_quiz2', 'score_finalexam']
            if data['update_field'] not in allowed_fields:
                return error_response(f"Invalid update_field. Must be one of: {', '.join(allowed_fields)}", None, 400)
            
            # Step 5: 驗證分數值
            is_valid_score, error_msg = ValidationService.validate_score_value(str(data['score_value']))
            if not is_valid_score:
                return error_response(error_msg, None, 400)
            
            # Step 6: 查詢是否已有成績記錄
            existing_score = SqlDbBusinessService.get_entity(Score, 'f_student_uuid', data['f_student_uuid'])
            
            timestamp = TimestampService.get_current_timestamp()
            
            if existing_score:
                # 更新現有成績
                update_data = {
                    data['update_field']: str(data['score_value']),
                    'score_updated_at': timestamp
                }
                updated_score = SqlDbBusinessService.update_entity(existing_score, update_data)
                output = ScoreReadSerializer(updated_score).data
                message = "Score updated successfully"
            else:
                # 創建新成績記錄
                score_uuid = UuidService.generate_score_uuid(student.student_semester)
                score_data = {
                    'score_uuid': score_uuid,
                    'f_student_uuid': data['f_student_uuid'],
                    'score_quiz1': '',
                    'score_midterm': '',
                    'score_quiz2': '',
                    'score_finalexam': '',
                    'score_total': '',
                    'score_created_at': timestamp,
                    'score_updated_at': timestamp,
                }
                score_data[data['update_field']] = str(data['score_value'])
                new_score = SqlDbBusinessService.create_entity(Score, score_data)
                output = ScoreReadSerializer(new_score).data
                message = "Score created successfully"
            
            logger.info(f"Score operation successful for student: {data['f_student_uuid']}")
            return success_response(output, message, 201)
            
        except json.JSONDecodeError:
            return error_response("Invalid JSON format", None, 400)
        except Exception as e:
            logger.error(f"Error creating/updating score: {str(e)}")
            return error_response(f"Unknown error: {str(e)}", None, 500)
    
    @staticmethod
    @csrf_exempt
    @require_http_methods(["POST"])
    @transaction.atomic
    def update(request):
        """
        更新分數
        POST /api/v0.1/Calculus_oom/Calculus_metadata/Score_MetadataWriter/update
        """
        try:
            # Step 1: 解析請求
            data = json.loads(request.body)
            logger.info(f"Updating score with data: {data}")
            
            # Step 2: 驗證必要欄位
            is_valid, missing_keys = ValidationService.validate_required_keys(
                data, ['score_uuid', 'update_field', 'score_value']
            )
            if not is_valid:
                return error_response(f"Missing required keys: {missing_keys}", None, 400)
            
            # Step 3: 查詢成績
            score = SqlDbBusinessService.get_entity(Score, 'score_uuid', data['score_uuid'])
            if not score:
                return error_response("Score not found", None, 404)
            
            # Step 4: 驗證分數欄位
            allowed_fields = ['score_quiz1', 'score_midterm', 'score_quiz2', 'score_finalexam']
            if data['update_field'] not in allowed_fields:
                return error_response(f"Invalid update_field. Must be one of: {', '.join(allowed_fields)}", None, 400)
            
            # Step 5: 驗證分數值
            is_valid_score, error_msg = ValidationService.validate_score_value(str(data['score_value']))
            if not is_valid_score:
                return error_response(error_msg, None, 400)
            
            # Step 6: 更新分數
            update_data = {
                data['update_field']: str(data['score_value']),
                'score_updated_at': TimestampService.get_current_timestamp()
            }
            updated_score = SqlDbBusinessService.update_entity(score, update_data)
            
            # Step 7: 格式化輸出
            output = ScoreReadSerializer(updated_score).data
            logger.info(f"Score updated successfully: {data['score_uuid']}")
            
            return success_response(output, "Score updated successfully", 200)
            
        except json.JSONDecodeError:
            return error_response("Invalid JSON format", None, 400)
        except Exception as e:
            logger.error(f"Error updating score: {str(e)}")
            return error_response(f"Unknown error: {str(e)}", None, 500)
    
    @staticmethod
    @csrf_exempt
    @require_http_methods(["POST"])
    @transaction.atomic
    def delete(request):
        """
        刪除分數
        POST /api/v0.1/Calculus_oom/Calculus_metadata/Score_MetadataWriter/delete
        """
        try:
            # Step 1: 解析請求
            data = json.loads(request.body)
            logger.info(f"Deleting score with data: {data}")
            
            # Step 2: 驗證必要欄位
            is_valid, missing_keys = ValidationService.validate_required_keys(data, ['score_uuid'])
            if not is_valid:
                return error_response(f"Missing required keys: {missing_keys}", None, 400)
            
            # Step 3: 查詢成績
            score = SqlDbBusinessService.get_entity(Score, 'score_uuid', data['score_uuid'])
            score = SqlDbBusinessService.get_entity(Score, 'score_uuid', data['uid'])
            if not score:
                return error_response("Score not found", None, 404)
            
            # Step 4: 刪除成績
            SqlDbBusinessService.delete_entity(score)
            
            logger.info(f"Score deleted successfully: {data['uid']}")
            return success_response(None, "Score deleted successfully", 200)
            
        except json.JSONDecodeError:
            return error_response("Invalid JSON format", None, 400)
        except Exception as e:
            logger.error(f"Error deleting score: {str(e)}")
            return error_response(f"Unknown error: {str(e)}", None, 500)
    
    @staticmethod
    @csrf_exempt
    @require_http_methods(["POST"])
    def read(request):
        """
        查詢分數
        POST /api/v0.1/Calculus_oom/Calculus_metadata/Score_MetadataWriter/read
        """
        try:
            # Step 1: 解析請求
            data = json.loads(request.body)
            logger.info(f"Reading scores with filters: {data}")
            
            # Step 2: 查詢成績
            if 'score_uuid' in data:
                score = SqlDbBusinessService.get_entity(Score, 'score_uuid', data['score_uuid'])
                if not score:
                    return error_response("Score not found", None, 404)
                output = ScoreReadSerializer(score).data
            elif 'f_student_uuid' in data:
                score = SqlDbBusinessService.get_entity(Score, 'f_student_uuid', data['f_student_uuid'])
                if not score:
                    return error_response("Score not found", None, 404)
                output = ScoreReadSerializer(score).data
            elif data:
                scores = SqlDbBusinessService.get_entities(Score, data)
                output = ScoreReadSerializer(scores, many=True).data
            else:
                scores = SqlDbBusinessService.get_entities(Score, {})
                output = ScoreReadSerializer(scores, many=True).data
            
            logger.info(f"Scores retrieved successfully")
            return success_response(output, "Scores retrieved successfully", 200)
            
        except json.JSONDecodeError:
            return error_response("Invalid JSON format", None, 400)
        except Exception as e:
            logger.error(f"Error reading scores: {str(e)}")
            return error_response(f"Unknown error: {str(e)}", None, 500)
    
    @staticmethod
    @csrf_exempt
    @require_http_methods(["POST"])
    @transaction.atomic
    def calculation_final(request):
        """
        計算期末總成績
        POST /api/v0.1/Calculus_oom/Calculus_metadata/Score_MetadataWriter/calculation_final
        """
        try:
            # Step 1: 解析請求
            data = json.loads(request.body)
            logger.info(f"Calculating final scores for semester: {data}")
            
            # Step 2: 驗證必要欄位
            is_valid, missing_keys = ValidationService.validate_required_keys(data, ['test_semester', 'passing_score'])
            if not is_valid:
                return error_response(f"Missing required keys: {missing_keys}", None, 400)
            
            semester = data['test_semester']
            passing_threshold = float(data['passing_score'])
            
            # Step 3: 獲取該學期所有考試權重
            tests = SqlDbBusinessService.get_entities(Test, {'test_semester': semester})
            if not tests:
                return error_response("No tests found for this semester", None, 404)
            
            weights = {}
            for test in tests:
                if test.test_weight:
                    weights[test.test_name] = float(test.test_weight)
            
            if not weights or sum(weights.values()) != 1.0:
                return error_response("Test weights invalid or not sum to 1.0", None, 400)
            
            # Step 4: 獲取該學期所有學生
            students = SqlDbBusinessService.get_entities(Students, {'student_semester': semester})
            
            updated_count = 0
            for student in students:
                # 跳過二退學生
                if student.student_status == '二退':
                    continue
                
                # 獲取學生成績
                score = SqlDbBusinessService.get_entity(Score, 'f_student_uuid', student.student_uuid)
                if not score:
                    continue
                
                # 計算總分
                scores_dict = {
                    '第一次小考': score.score_quiz1,
                    '期中考': score.score_midterm,
                    '第二次小考': score.score_quiz2,
                    '期末考': score.score_finalexam,
                }
                
                # 檢查是否所有成績都已填寫
                if not all(scores_dict.values()):
                    continue
                
                # 轉換為浮點數並計算加權總分
                scores_float = {k: float(v) for k, v in scores_dict.items() if v}
                total_score = CalculationService.calculate_weighted_total(scores_float, weights)
                
                # 更新總分
                update_data = {
                    'score_total': str(round(total_score, 2)),
                    'score_updated_at': TimestampService.get_current_timestamp()
                }
                SqlDbBusinessService.update_entity(score, update_data)
                
                # 更新學生狀態
                is_passing = CalculationService.check_passing(total_score, passing_threshold)
                new_status = '修業完畢' if is_passing else '被當'
                student_update = {
                    'student_status': new_status,
                    'student_updated_at': TimestampService.get_current_timestamp()
                }
                SqlDbBusinessService.update_entity(student, student_update)
                
                updated_count += 1
            
            logger.info(f"Final scores calculated for {updated_count} students")
            return success_response(
                {'updated_count': updated_count},
                f"Final scores calculated successfully for {updated_count} students",
                200
            )
            
        except json.JSONDecodeError:
            return error_response("Invalid JSON format", None, 400)
        except Exception as e:
            logger.error(f"Error calculating final scores: {str(e)}")
            return error_response(f"Unknown error: {str(e)}", None, 500)
    
    @staticmethod
    @csrf_exempt
    @require_http_methods(["POST"])
    def test_score(request):
        """
        計算考試統計數據（平均、中位數）
        POST /api/v0.1/Calculus_oom/Calculus_metadata/Score_MetadataWriter/test_score
        """
        try:
            # Step 1: 解析請求
            data = json.loads(request.body)
            logger.info(f"Calculating test statistics: {data}")
            
            # Step 2: 驗證必要欄位
            is_valid, missing_keys = ValidationService.validate_required_keys(
                data, ['score_semester', 'score_field']
            )
            if not is_valid:
                return error_response(f"Missing required keys: {missing_keys}", None, 400)
            
            semester = data['score_semester']
            score_field = data['score_field']
            exclude_empty = data.get('exclude_empty', True)
            
            # Step 3: 驗證分數欄位
            allowed_fields = ['score_quiz1', 'score_midterm', 'score_quiz2', 'score_finalexam']
            if score_field not in allowed_fields:
                return error_response(f"Invalid score_field. Must be one of: {', '.join(allowed_fields)}", None, 400)
            
            # Step 4: 獲取該學期所有學生的成績
            students = SqlDbBusinessService.get_entities(Students, {'student_semester': semester})
            student_uuids = [s.student_uuid for s in students if s.student_status != '二退']
            
            scores = []
            for student_uuid in student_uuids:
                score = SqlDbBusinessService.get_entity(Score, 'f_student_uuid', student_uuid)
                if score:
                    score_value = getattr(score, score_field, '')
                    if score_value and score_value.strip():
                        try:
                            scores.append(float(score_value))
                        except ValueError:
                            continue
            
            if not scores:
                return error_response("No valid scores found", None, 404)
            
            # Step 5: 計算統計數據
            average = CalculationService.calculate_average(scores)
            median = CalculationService.calculate_median(scores)
            
            output = {
                'semester': semester,
                'score_field': score_field,
                'total_count': len(scores),
                'average': round(average, 2),
                'median': round(median, 2),
            }
            
            logger.info(f"Test statistics calculated successfully")
            return success_response(output, "Test statistics calculated successfully", 200)
            
        except json.JSONDecodeError:
            return error_response("Invalid JSON format", None, 400)
        except Exception as e:
            logger.error(f"Error calculating test statistics: {str(e)}")
            return error_response(f"Unknown error: {str(e)}", None, 500)
