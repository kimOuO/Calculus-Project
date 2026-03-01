"""
TestFiledata Actor - 考卷檔案管理 (NonSQL / GridFS)
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

logger = logging.getLogger(__name__)


class TestFiledataActor:
    """考卷檔案 Actor - 處理 NonSQL 檔案存儲業務（GridFS 二進位存儲）"""

    ALLOWED_ASSET_TYPES = ['paper', 'test_pic', 'histogram', 'test_pic_histogram']
    COLLECTION_NAME = 'test_pic_information'

    # asset_type → MongoDB GridFS ID 欄位名稱對應
    _GRIDFS_FIELD = {
        'paper': 'test_pic_gridfs_id',
        'test_pic': 'test_pic_gridfs_id',
        'histogram': 'test_pic_histogram_gridfs_id',
        'test_pic_histogram': 'test_pic_histogram_gridfs_id',
    }
    # 舊路徑欄位（向下相容讀取）
    _LEGACY_PATH_FIELD = {
        'paper': 'test_pic',
        'test_pic': 'test_pic',
        'histogram': 'test_pic_histogram',
        'test_pic_histogram': 'test_pic_histogram',
    }

    @staticmethod
    @csrf_exempt
    @require_http_methods(["POST"])
    def create(request):
        """
        上傳考卷檔案/直方圖（binary → GridFS）
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

            # Step 5: 驗證 test_uuid 並決定 file_uuid
            test = SqlDbBusinessService.get_entity(Test, 'test_uuid', test_uuid)
            if not test:
                return error_response("Test not found", None, 404)

            if test.pt_opt_score_uuid:
                file_uuid = test.pt_opt_score_uuid
                existing_doc = NoSqlDbBusinessService.get_document(
                    TestFiledataActor.COLLECTION_NAME,
                    {'test_pic_uuid': file_uuid}
                )
                is_update = existing_doc is not None
            else:
                file_uuid = UuidService.generate_test_pic_uuid(test_uuid[:8], "file")
                existing_doc = None
                is_update = False

            # Step 6: 上傳第一個檔案至 GridFS
            uploaded_file = uploaded_files[0]
            file_data = uploaded_file.read()
            content_type = uploaded_file.content_type or 'application/octet-stream'
            gridfs_filename = f"{file_uuid}_{uploaded_file.name}"

            gridfs_id = NoSqlDbBusinessService.upload_file_to_gridfs(
                gridfs_filename, file_data, content_type
            )
            logger.info(f"File uploaded to GridFS: {gridfs_id} ({gridfs_filename})")

            # Step 7: 更新或建立 MongoDB 文檔
            timestamp = TimestampService.get_current_timestamp()
            gridfs_field = TestFiledataActor._GRIDFS_FIELD[asset_type]

            if is_update:
                # 刪除舊 GridFS 檔案（若存在）
                old_gridfs_id = existing_doc.get(gridfs_field, '')
                if old_gridfs_id:
                    try:
                        NoSqlDbBusinessService.delete_file_from_gridfs(old_gridfs_id)
                    except Exception:
                        pass  # 舊檔不存在時忽略

                NoSqlDbBusinessService.update_document(
                    TestFiledataActor.COLLECTION_NAME,
                    {'test_pic_uuid': file_uuid},
                    {gridfs_field: gridfs_id, 'pic_updated_at': timestamp}
                )
                inserted_id = existing_doc['_id']
            else:
                document = {
                    'test_pic_uuid': file_uuid,
                    'test_uuid': test.test_uuid,
                    'test_semester': test.test_semester,
                    'test_name': test.test_name,
                    'test_pic_gridfs_id': '',
                    'test_pic_histogram_gridfs_id': '',
                    'pic_created_at': timestamp,
                    'pic_updated_at': timestamp,
                }
                document[gridfs_field] = gridfs_id

                inserted_id = NoSqlDbBusinessService.create_document(
                    TestFiledataActor.COLLECTION_NAME,
                    document
                )

            # Step 8: 更新 Test 表的 pt_opt_score_uuid 並自動更新狀態
            update_sql = {}
            if not test.pt_opt_score_uuid:
                update_sql['pt_opt_score_uuid'] = file_uuid

            if asset_type in ['paper', 'test_pic']:
                if test.test_states == '尚未出考卷':
                    update_sql['test_states'] = '考卷完成'
                    update_sql['test_updated_at'] = timestamp
                    logger.info(f"Auto-updating test status to '考卷完成' for test: {test_uuid}")
            elif asset_type in ['histogram', 'test_pic_histogram']:
                if test.test_states == '考卷完成':
                    update_sql['test_states'] = '考卷成績結算'
                    update_sql['test_updated_at'] = timestamp
                    logger.info(f"Auto-updating test status to '考卷成績結算' for test: {test_uuid}")

            if update_sql:
                SqlDbBusinessService.update_entity(test, update_sql)

            output = {
                'file_uuid': file_uuid,
                'asset_type': asset_type,
                'file_count': len(uploaded_files),
                'gridfs_id': gridfs_id,
                'mongodb_id': str(inserted_id),
                'test_states': test.test_states if 'test_states' not in update_sql else update_sql['test_states'],
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
        讀取考卷檔案（優先從 GridFS 讀取，向下相容舊路徑）
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

            # Step 4: 從 MongoDB 查詢文檔
            document = NoSqlDbBusinessService.get_document(
                TestFiledataActor.COLLECTION_NAME,
                {'test_pic_uuid': file_uuid}
            )

            if not document:
                return error_response("Source not found", None, 404)

            gridfs_field = TestFiledataActor._GRIDFS_FIELD[asset_type]
            legacy_field = TestFiledataActor._LEGACY_PATH_FIELD[asset_type]

            gridfs_id = document.get(gridfs_field, '')
            legacy_path = document.get(legacy_field, '')

            # Step 5a: 從 GridFS 讀取（優先）
            if gridfs_id:
                file_data, filename, content_type = NoSqlDbBusinessService.download_file_from_gridfs(gridfs_id)
                response = HttpResponse(file_data, content_type=content_type)
                response['Content-Disposition'] = f'inline; filename="{filename}"'
                logger.info(f"File retrieved from GridFS: {file_uuid} ({gridfs_id}), type: {content_type}")
                return response

            # Step 5b: 向下相容 — 從本地磁碟讀取舊格式檔案
            if legacy_path:
                if not os.path.exists(legacy_path):
                    return error_response("File not found on disk", None, 404)

                file_ext = os.path.splitext(legacy_path)[1].lower()
                content_type_map = {
                    '.pdf': 'application/pdf',
                    '.jpg': 'image/jpeg',
                    '.jpeg': 'image/jpeg',
                    '.png': 'image/png',
                    '.gif': 'image/gif',
                }
                content_type = content_type_map.get(file_ext, 'application/octet-stream')
                response = FileResponse(open(legacy_path, 'rb'))
                response['Content-Type'] = content_type
                response['Content-Disposition'] = f'inline; filename="{os.path.basename(legacy_path)}"'
                logger.info(f"File retrieved from disk (legacy): {file_uuid}, type: {content_type}")
                return response

            return error_response("ClientError: asset_type mismatch with file_uuid", None, 400)

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
        更新考卷檔案（替換，舊 GridFS 檔案自動刪除）
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

            gridfs_field = TestFiledataActor._GRIDFS_FIELD[asset_type]

            # Step 5: 上傳新檔案至 GridFS
            file_data = uploaded_file.read()
            content_type = uploaded_file.content_type or 'application/octet-stream'
            gridfs_filename = f"{file_uuid}_{uploaded_file.name}"
            new_gridfs_id = NoSqlDbBusinessService.upload_file_to_gridfs(
                gridfs_filename, file_data, content_type
            )

            # Step 6: 刪除舊 GridFS 檔案（若存在）
            old_gridfs_id = document.get(gridfs_field, '')
            if old_gridfs_id:
                try:
                    NoSqlDbBusinessService.delete_file_from_gridfs(old_gridfs_id)
                except Exception:
                    pass

            # Step 7: 更新 MongoDB
            NoSqlDbBusinessService.update_document(
                TestFiledataActor.COLLECTION_NAME,
                {'test_pic_uuid': file_uuid},
                {
                    gridfs_field: new_gridfs_id,
                    'pic_updated_at': TimestampService.get_current_timestamp(),
                }
            )

            logger.info(f"File updated successfully: {file_uuid}, new GridFS ID: {new_gridfs_id}")
            return success_response(
                {'file_uuid': file_uuid, 'gridfs_id': new_gridfs_id},
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
        刪除考卷檔案（同時清除 GridFS 二進位資料）
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

            gridfs_field = TestFiledataActor._GRIDFS_FIELD[asset_type]

            # Step 5: 刪除 GridFS 檔案
            gridfs_id = document.get(gridfs_field, '')
            if gridfs_id:
                try:
                    NoSqlDbBusinessService.delete_file_from_gridfs(gridfs_id)
                    logger.info(f"GridFS file deleted: {gridfs_id}")
                except Exception as e:
                    logger.warning(f"Could not delete GridFS file {gridfs_id}: {e}")

            # Step 6: 更新 MongoDB（清除該欄位）
            NoSqlDbBusinessService.update_document(
                TestFiledataActor.COLLECTION_NAME,
                {'test_pic_uuid': file_uuid},
                {
                    gridfs_field: '',
                    'pic_updated_at': TimestampService.get_current_timestamp(),
                }
            )

            logger.info(f"File deleted successfully: {file_uuid}")
            return success_response(None, "File deleted successfully", 200)

        except json.JSONDecodeError:
            return error_response("Invalid JSON format", None, 400)
        except Exception as e:
            logger.error(f"Error deleting file: {str(e)}")
            return error_response(f"Unknown error: {str(e)}", None, 500)
