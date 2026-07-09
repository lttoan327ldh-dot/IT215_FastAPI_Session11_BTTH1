from datetime import datetime, timezone
from typing import Any, Optional
from fastapi.responses import JSONResponse


def build_response_body(
    status_code: int,
    message: str,
    error: Optional[str],
    data: Any,
    path: str,
) -> dict:
    """Xây dựng payload JSON theo cấu trúc chuẩn 6 trường."""
    return {
        "statusCode": status_code,
        "message": message,
        "error": error,
        "data": data,
        "path": path,
        "timestamp": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
    }


def json_response(
    status_code: int,
    message: str,
    error: Optional[str],
    data: Any,
    path: str,
) -> JSONResponse:
    """Trả về JSONResponse đã được bọc đúng cấu trúc chuẩn."""
    return JSONResponse(
        status_code=status_code,
        content=build_response_body(status_code, message, error, data, path),
    )
