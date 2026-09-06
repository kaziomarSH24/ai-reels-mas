from typing import Any, Optional
from fastapi.responses import JSONResponse

class ApiResponse:
    """
    Standardize the JSON response format for the entire API.
    Provides response_success and response_error methods EXACTLY like the Laravel boilerplate.
    """
    @staticmethod
    def response_success(message: str, data: Any = None, status_code: int = 200):
        return JSONResponse(
            status_code=status_code,
            content={
                "ok": True,
                "message": message,
                "data": data if data is not None else []
            }
        )

    @staticmethod
    def response_error(message: str, errors: Optional[Any] = None, status_code: int = 400):
        content = {
            "ok": False,
            "message": message,
        }
        if errors is not None:
            content["errors"] = errors
            
        return JSONResponse(
            status_code=status_code,
            content=content
        )
