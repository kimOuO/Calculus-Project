"""
TestPicInformation Model - NoSQL Database (MongoDB)
歷年考卷照片資訊表

Note: This is a representation class for MongoDB documents.
Actual CRUD operations are handled by NoSqlDbBusinessService.
"""


class TestPicInformation:
    """考卷照片資訊 Model (MongoDB) - 文檔結構定義"""
    
    # 此類別僅用於文檔結構說明，實際操作使用 NoSqlDbBusinessService
    
    COLLECTION_NAME = 'test_pic_information'
    
    SCHEMA = {
        '_id': 'ObjectId (MongoDB auto-generated)',
        'test_pic_uuid': 'str - 唯一識別碼',
        'test_pic_histogram': 'str - 考卷十分為一級距的直方圖的本地路徑',
        'test_pic': 'str - 考卷照片的本地路徑',
        'pic_created_at': 'str - 建立時間',
        'pic_updated_at': 'str - 更新時間',
    }
    
    @staticmethod
    def create_document(test_pic_uuid: str, test_pic: str = "", test_pic_histogram: str = "", 
                       pic_created_at: str = "", pic_updated_at: str = "") -> dict:
        """
        創建文檔結構
        
        Returns:
            dict: MongoDB 文檔
        """
        return {
            'test_pic_uuid': test_pic_uuid,
            'test_pic': test_pic,
            'test_pic_histogram': test_pic_histogram,
            'pic_created_at': pic_created_at,
            'pic_updated_at': pic_updated_at,
        }
    
    def __str__(self):
        return f"TestPicInformation Schema Definition"
