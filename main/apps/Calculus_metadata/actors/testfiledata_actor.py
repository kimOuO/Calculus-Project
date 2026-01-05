"""
TestFiledata Actor - 考卷檔案管理 (NonSQL)
"""
import json
import logging
import os
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.http import FileResponse, HttpResponse
from django.db import transaction

from main.apps.Calculus_metadata.services.common import UuidService, TimestampService, ValidationService
from main.apps.Calculus_metadata.services.business import NoSqlDbBusinessService, SqlDbBusinessService
from main.apps.Calculus_metadata.models import Test
from main.utils.response import success_response, error_response
from django.conf import settings

logger = logging.getLogger(__name__)


class TestFiledataActor:
    """考卷檔案 Actor - 處理 NonSQL 檔案存儲業務（純檔案管理，不修改 SQL 狀態）"""
    
    ALLOWED_ASSET_TYPES = ['paper', 'test_pic', 'histogram', 'test_pic_histogram']
    COLLECTION_NAME = 'test_pic_information'
    
    @staticmethod
    @csrf_exempt
    @require_http_methods(["POST"])
    def create(request):
        """
        上傳考卷檔案/直方圖
        POST /api/v0.1/Calculus_oom/Calculus_metadata/test-filedata/create
        """
        try:
            # Step 1: 解析請求（multipart form-data）
            test_uuid = request.POST.get('test_uuid')
            asset_type = request.POST.get('asset_type')
            uploaded_files = request.FILES.getlist('file')
            
            logger.info(f"Uploading files for test: {test_uuid}, asset_type: {asset_type}")
            
            # Step 2: 驗證必要欄位
            if not test_uuid or not asset_type:
                return error_response("Missing required keys: test_uuid, asset_type", None, 400)
            
            # Step 3: 驗證 asset_type
            if asset_type not in TestFiledataActor.ALLOWED_ASSET_TYPES:
                return error_response(
                    f"ClientError: asset_type not allowed. Must be one of: {', '.join(TestFiledataActor.ALLOWED_ASSET_TYPES)}",
                    None,
                    400
                )
            
            # Step 4: 驗證檔案是否存在
            if not uploaded_files:
                return error_response("No files uploaded", None, 400)
            
            # Step 4.5: 驗證 test_uuid 是否存在並獲取或創建 file_uuid
            test = SqlDbBusinessService.get_entity(Test, 'test_uuid', test_uuid)
            if not test:
                return error_response("Test not found", None, 404)
            
            # 如果該考試已經有 file_uuid，則使用現有的；否則創建新的
            if test.pt_opt_score_uuid:
                file_uuid = test.pt_opt_score_uuid
                # 檢查 MongoDB 中是否存在該文檔
                existing_doc = NoSqlDbBusinessService.get_document(
                    TestFiledataActor.COLLECTION_NAME,
                    {'test_pic_uuid': file_uuid}
                )
                is_update = existing_doc is not None
            else:
                file_uuid = UuidService.generate_test_pic_uuid(test_uuid[:8], "file")
                is_update = False
            
            # Step 5: 生成時間戳
            timestamp = TimestampService.get_current_timestamp()
            
            # Step 6: 儲存檔案到本地
            upload_dir = settings.UPLOAD_DIR
            os.makedirs(upload_dir, exist_ok=True)
            
            file_paths = []
            for uploaded_file in uploaded_files:
                file_name = f"{file_uuid}_{uploaded_file.name}"
                file_path = os.path.join(upload_dir, file_name)
                
                with open(file_path, 'wb+') as destination:
                    for chunk in uploaded_file.chunks():
                        destination.write(chunk)
                
                file_paths.append(file_path)
                logger.info(f"File saved: {file_path}")
            
            # Step 7: 儲存或更新檔案資訊到 MongoDB
            if is_update:
                # 更新現有文檔
                update_data = {'pic_updated_at': timestamp}
                
                if asset_type in ['paper', 'test_pic']:
                    update_data['test_pic'] = file_paths[0] if file_paths else ''
                elif asset_type in ['histogram', 'test_pic_histogram']:
                    update_data['test_pic_histogram'] = file_paths[0] if file_paths else ''
                
                NoSqlDbBusinessService.update_document(
                    TestFiledataActor.COLLECTION_NAME,
                    {'test_pic_uuid': file_uuid},
                    update_data
                )
                inserted_id = str(existing_doc['_id'])
            else:
                # 創建新文檔
                document = {
                    'test_pic_uuid': file_uuid,
                    'test_pic': '',
                    'test_pic_histogram': '',
                    'pic_created_at': timestamp,
                    'pic_updated_at': timestamp,
                }
                
                # 根據 asset_type 決定存儲位置
                if asset_type in ['paper', 'test_pic']:
                    document['test_pic'] = file_paths[0] if file_paths else ''
                elif asset_type in ['histogram', 'test_pic_histogram']:
                    document['test_pic_histogram'] = file_paths[0] if file_paths else ''
                
                # 儲存到 MongoDB
                inserted_id = NoSqlDbBusinessService.create_document(
                    TestFiledataActor.COLLECTION_NAME,
                    document
                )
            
            # Step 8: 更新 Test 表的 pt_opt_score_uuid 並自動更新狀態
            update_data = {}
            if not test.pt_opt_score_uuid:
                update_data['pt_opt_score_uuid'] = file_uuid
            
            # 自動狀態更新邏輯
            if asset_type in ['paper', 'test_pic']:
                # 上傳考卷時，自動將狀態從「尚未出考卷」更新為「考卷完成」
                if test.test_states == '尚未出考卷':
                    update_data['test_states'] = '考卷完成'
                    update_data['test_updated_at'] = timestamp
                    logger.info(f"Auto-updating test status to '考卷完成' for test: {test_uuid}")
            elif asset_type in ['histogram', 'test_pic_histogram']:
                # 上傳直方圖時，自動將狀態從「考卷完成」更新為「考卷成績結算」
                if test.test_states == '考卷完成':
                    update_data['test_states'] = '考卷成績結算'
                    update_data['test_updated_at'] = timestamp
                    logger.info(f"Auto-updating test status to '考卷成績結算' for test: {test_uuid}")
            
            if update_data:
                SqlDbBusinessService.update_entity(test, update_data)
            
            output = {
                'file_uuid': file_uuid,
                'asset_type': asset_type,
                'file_count': len(file_paths),
                'mongodb_id': inserted_id,
                'test_states': test.test_states if 'test_states' not in update_data else update_data['test_states']
            }
            
            logger.info(f"Files uploaded successfully: {file_uuid}")
            return success_response(output, "Files uploaded successfully", 201)
            
        except Exception as e:
            logger.error(f"Error uploading files: {str(e)}")
            return error_response(f"Unknown error: {str(e)}", None, 500)
    
    @staticmethod
    @csrf_exempt
    @require_http_methods(["POST"])
    def read(request):
        """
        讀取考卷檔案
        POST /api/v0.1/Calculus_oom/Calculus_metadata/test-filedata/read
        """
        try:
            # Step 1: 解析請求
            data = json.loads(request.body)
            logger.info(f"Reading file with data: {data}")
            
            # Step 2: 驗證必要欄位
            is_valid, missing_keys = ValidationService.validate_required_keys(
                data, ['test_pic_uuid', 'asset_type']
            )
            if not is_valid:
                return error_response(f"Missing required keys: {missing_keys}", None, 400)
            
            file_uuid = data['test_pic_uuid']
            asset_type = data['asset_type']
            
            # Step 3: 驗證 asset_type
            if asset_type not in TestFiledataActor.ALLOWED_ASSET_TYPES:
                return error_response("ClientError: asset_type not allowed", None, 400)
            
            # Step 4: 從 MongoDB 查詢檔案資訊
            document = NoSqlDbBusinessService.get_document(
                TestFiledataActor.COLLECTION_NAME,
                {'test_pic_uuid': file_uuid}
            )
            
            if not document:
                return error_response("Source not found", None, 404)
            
            # Step 5: 驗證 asset_type 是否匹配
            file_path = None
            if asset_type in ['paper', 'test_pic']:
                file_path = document.get('test_pic')
            elif asset_type in ['histogram', 'test_pic_histogram']:
                file_path = document.get('test_pic_histogram')
            
            if not file_path:
                return error_response("ClientError: asset_type mismatch with file_uuid", None, 400)
            
            # Step 6: 檢查檔案是否存在
            if not os.path.exists(file_path):
                return error_response("File not found on disk", None, 404)
            
            # Step 7: 根據文件擴展名判斷 Content-Type
            file_ext = os.path.splitext(file_path)[1].lower()
            content_type_map = {
                '.pdf': 'application/pdf',
                '.jpg': 'image/jpeg',
                '.jpeg': 'image/jpeg',
                '.png': 'image/png',
                '.gif': 'image/gif',
                '.txt': 'text/plain',
            }
            content_type = content_type_map.get(file_ext, 'application/octet-stream')
            
            # Step 8: 返回檔案
            response = FileResponse(open(file_path, 'rb'))
            response['Content-Type'] = content_type
            response['Content-Disposition'] = f'inline; filename="{os.path.basename(file_path)}"'
            
            logger.info(f"File retrieved successfully: {file_uuid}, type: {content_type}")
            return response
            
        except json.JSONDecodeError:
            return error_response("Invalid JSON format", None, 400)
        except Exception as e:
            logger.error(f"Error reading file: {str(e)}")
            return error_response(f"Unknown error: {str(e)}", None, 500)
    
    @staticmethod
    @csrf_exempt
    @require_http_methods(["POST"])
    def update(request):
        """
        更新考卷檔案（替換）
        POST /api/v0.1/Calculus_oom/Calculus_metadata/test-filedata/update
        """
        try:
            # Step 1: 解析請求
            file_uuid = request.POST.get('uid')
            asset_type = request.POST.get('asset_type')
            uploaded_file = request.FILES.get('file')
            
            logger.info(f"Updating file: {file_uuid}, asset_type: {asset_type}")
            
            # Step 2: 驗證必要欄位
            if not file_uuid or not asset_type or not uploaded_file:
                return error_response("Missing required keys: uid, asset_type, file", None, 400)
            
            # Step 3: 驗證 asset_type
            if asset_type not in TestFiledataActor.ALLOWED_ASSET_TYPES:
                return error_response("ClientError: asset_type not allowed", None, 400)
            
            # Step 4: 查詢 MongoDB 文檔
            document = NoSqlDbBusinessService.get_document(
                TestFiledataActor.COLLECTION_NAME,
                {'test_pic_uuid': file_uuid}
            )
            
            if not document:
                return error_response("Source not found", None, 404)
            
            # Step 5: 刪除舊檔案
            old_file_path = None
            if asset_type in ['paper', 'test_pic']:
                old_file_path = document.get('test_pic')
            elif asset_type in ['histogram', 'test_pic_histogram']:
                old_file_path = document.get('test_pic_histogram')
            
            if old_file_path and os.path.exists(old_file_path):
                os.remove(old_file_path)
                logger.info(f"Old file deleted: {old_file_path}")
            
            # Step 6: 儲存新檔案
            upload_dir = settings.UPLOAD_DIR
            file_name = f"{file_uuid}_{uploaded_file.name}"
            new_file_path = os.path.join(upload_dir, file_name)
            
            with open(new_file_path, 'wb+') as destination:
                for chunk in uploaded_file.chunks():
                    destination.write(chunk)
            
            # Step 7: 更新 MongoDB
            update_data = {
                'pic_updated_at': TimestampService.get_current_timestamp()
            }
            
            if asset_type in ['paper', 'test_pic']:
                update_data['test_pic'] = new_file_path
            elif asset_type in ['histogram', 'test_pic_histogram']:
                update_data['test_pic_histogram'] = new_file_path
            
            NoSqlDbBusinessService.update_document(
                TestFiledataActor.COLLECTION_NAME,
                {'test_pic_uuid': file_uuid},
                update_data
            )
            
            logger.info(f"File updated successfully: {file_uuid}")
            return success_response(
                {'file_uuid': file_uuid, 'new_file_path': new_file_path},
                "File updated successfully",
                200
            )
            
        except Exception as e:
            logger.error(f"Error updating file: {str(e)}")
            return error_response(f"Unknown error: {str(e)}", None, 500)
    
    @staticmethod
    @csrf_exempt
    @require_http_methods(["POST"])
    def delete(request):
        """
        刪除考卷檔案
        POST /api/v0.1/Calculus_oom/Calculus_metadata/test-filedata/delete
        """
        try:
            # Step 1: 解析請求
            data = json.loads(request.body)
            logger.info(f"Deleting file with data: {data}")
            
            # Step 2: 驗證必要欄位
            is_valid, missing_keys = ValidationService.validate_required_keys(
                data, ['test_pic_uuid', 'asset_type']
            )
            if not is_valid:
                return error_response(f"Missing required keys: {missing_keys}", None, 400)
            
            file_uuid = data['test_pic_uuid']
            asset_type = data['asset_type']
            
            # Step 3: 驗證 asset_type
            if asset_type not in TestFiledataActor.ALLOWED_ASSET_TYPES:
                return error_response("ClientError: asset_type not allowed", None, 400)
            
            # Step 4: 查詢 MongoDB 文檔
            document = NoSqlDbBusinessService.get_document(
                TestFiledataActor.COLLECTION_NAME,
                {'test_pic_uuid': file_uuid}
            )
            
            if not document:
                return error_response("Source not found", None, 404)
            
            # Step 5: 刪除檔案
            file_path = None
            if asset_type in ['paper', 'test_pic']:
                file_path = document.get('test_pic')
            elif asset_type in ['histogram', 'test_pic_histogram']:
                file_path = document.get('test_pic_histogram')
            
            if file_path and os.path.exists(file_path):
                os.remove(file_path)
                logger.info(f"File deleted from disk: {file_path}")
            
            # Step 6: 刪除 MongoDB 文檔
            NoSqlDbBusinessService.delete_document(
                TestFiledataActor.COLLECTION_NAME,
                {'test_pic_uuid': file_uuid}
            )
            
            logger.info(f"File deleted successfully: {file_uuid}")
            return success_response(None, "File deleted successfully", 200)
            
        except json.JSONDecodeError:
            return error_response("Invalid JSON format", None, 400)
        except Exception as e:
            logger.error(f"Error deleting file: {str(e)}")
            return error_response(f"Unknown error: {str(e)}", None, 500)
