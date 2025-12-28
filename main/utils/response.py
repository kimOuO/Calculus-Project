"""
Response Utilities - 響應格式標準化
"""
from django.http import JsonResponse
from typing import Any, Optional, Dict


def success_response(data: Any = None, message: str = "Success", status_code: int = 200) -> JsonResponse:
    """
    成功響應格式
    
    Args:
        data: 響應數據
        message: 響應訊息
        status_code: HTTP 狀態碼
        
    Returns:
        JsonResponse
    """
    response_data = {
        "detail": message
    }
    
    if data is not None:
        response_data["data"] = data
    
    return JsonResponse(response_data, status=status_code, safe=False)


def error_response(message: str, errors: Optional[Dict] = None, status_code: int = 400) -> JsonResponse:
    """
    錯誤響應格式
    
    Args:
        message: 錯誤訊息
        errors: 詳細錯誤資訊
        status_code: HTTP 狀態碼
        
    Returns:
        JsonResponse
    """
    response_data = {
        "detail": message
    }
    
    if errors is not None:
        response_data["errors"] = errors
    
    return JsonResponse(response_data, status=status_code)


def paginated_response(
    data: list,
    page: int,
    page_size: int,
    total: int,
    message: str = "Success"
) -> JsonResponse:
    """
    分頁響應格式
    
    Args:
        data: 響應數據列表
        page: 當前頁碼
        page_size: 每頁數量
        total: 總數量
        message: 響應訊息
        
    Returns:
        JsonResponse
    """
    total_pages = (total + page_size - 1) // page_size
    
    response_data = {
        "detail": message,
        "data": data,
        "pagination": {
            "page": page,
            "page_size": page_size,
            "total": total,
            "total_pages": total_pages,
        }
    }
    
    return JsonResponse(response_data, status=200, safe=False)
