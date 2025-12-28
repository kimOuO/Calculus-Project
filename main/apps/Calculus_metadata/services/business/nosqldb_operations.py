"""
NoSQL Database Operations - MongoDB 通用操作服務
"""
from typing import Dict, Any, List, Optional
from pymongo import MongoClient
from pymongo.errors import PyMongoError
from main.utils.env_loader import get_env


class NoSqlDbBusinessService:
    """MongoDB 資料庫通用業務服務"""
    
    @staticmethod
    def get_connection():
        """
        獲取 MongoDB 連接
        
        Returns:
            MongoClient 實例
        """
        mongo_host = get_env("MONGO_HOST", "localhost")
        mongo_port = int(get_env("MONGO_PORT", "27017"))
        mongo_user = get_env("MONGO_USER", "")
        mongo_password = get_env("MONGO_PASSWORD", "")
        mongo_db = get_env("MONGO_DB", "calculus_nosql_db")
        
        if mongo_user and mongo_password:
            connection_string = f"mongodb://{mongo_user}:{mongo_password}@{mongo_host}:{mongo_port}/{mongo_db}?authSource=admin"
        else:
            connection_string = f"mongodb://{mongo_host}:{mongo_port}/{mongo_db}"
        
        return MongoClient(connection_string)
    
    @staticmethod
    def create_document(collection_name: str, document: Dict[str, Any]) -> str:
        """
        創建文檔
        
        Args:
            collection_name: 集合名稱
            document: 文檔數據
            
        Returns:
            插入的文檔 _id
        """
        try:
            client = NoSqlDbBusinessService.get_connection()
            db = client[get_env("MONGO_DB", "calculus_nosql_db")]
            collection = db[collection_name]
            result = collection.insert_one(document)
            return str(result.inserted_id)
        except PyMongoError as e:
            raise Exception(f"MongoDB create error: {str(e)}")
        finally:
            client.close()
    
    @staticmethod
    def get_document(collection_name: str, filters: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        查詢單個文檔
        
        Args:
            collection_name: 集合名稱
            filters: 查詢條件
            
        Returns:
            文檔數據或 None
        """
        try:
            client = NoSqlDbBusinessService.get_connection()
            db = client[get_env("MONGO_DB", "calculus_nosql_db")]
            collection = db[collection_name]
            document = collection.find_one(filters)
            if document:
                document['_id'] = str(document['_id'])
            return document
        except PyMongoError as e:
            raise Exception(f"MongoDB read error: {str(e)}")
        finally:
            client.close()
    
    @staticmethod
    def get_documents(collection_name: str, filters: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        查詢多個文檔
        
        Args:
            collection_name: 集合名稱
            filters: 查詢條件
            
        Returns:
            文檔列表
        """
        try:
            client = NoSqlDbBusinessService.get_connection()
            db = client[get_env("MONGO_DB", "calculus_nosql_db")]
            collection = db[collection_name]
            documents = list(collection.find(filters))
            for doc in documents:
                doc['_id'] = str(doc['_id'])
            return documents
        except PyMongoError as e:
            raise Exception(f"MongoDB read error: {str(e)}")
        finally:
            client.close()
    
    @staticmethod
    def update_document(collection_name: str, filters: Dict[str, Any], update_data: Dict[str, Any]) -> int:
        """
        更新文檔
        
        Args:
            collection_name: 集合名稱
            filters: 查詢條件
            update_data: 更新數據
            
        Returns:
            修改的文檔數量
        """
        try:
            client = NoSqlDbBusinessService.get_connection()
            db = client[get_env("MONGO_DB", "calculus_nosql_db")]
            collection = db[collection_name]
            result = collection.update_one(filters, {"$set": update_data})
            return result.modified_count
        except PyMongoError as e:
            raise Exception(f"MongoDB update error: {str(e)}")
        finally:
            client.close()
    
    @staticmethod
    def delete_document(collection_name: str, filters: Dict[str, Any]) -> int:
        """
        刪除文檔
        
        Args:
            collection_name: 集合名稱
            filters: 查詢條件
            
        Returns:
            刪除的文檔數量
        """
        try:
            client = NoSqlDbBusinessService.get_connection()
            db = client[get_env("MONGO_DB", "calculus_nosql_db")]
            collection = db[collection_name]
            result = collection.delete_one(filters)
            return result.deleted_count
        except PyMongoError as e:
            raise Exception(f"MongoDB delete error: {str(e)}")
        finally:
            client.close()
    
    @staticmethod
    def document_exists(collection_name: str, filters: Dict[str, Any]) -> bool:
        """
        檢查文檔是否存在
        
        Args:
            collection_name: 集合名稱
            filters: 查詢條件
            
        Returns:
            是否存在
        """
        try:
            client = NoSqlDbBusinessService.get_connection()
            db = client[get_env("MONGO_DB", "calculus_nosql_db")]
            collection = db[collection_name]
            return collection.count_documents(filters) > 0
        except PyMongoError as e:
            raise Exception(f"MongoDB check error: {str(e)}")
        finally:
            client.close()
