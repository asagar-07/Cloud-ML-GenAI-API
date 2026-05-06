from fastapi import Request
from fastapi.responses import JSONResponse
from app.core.logging import logger

class AppException(Exception):
    def __init__(self, message: str, status_code: int = 500):
        self.message = message
        self.status_code = status_code
        super().__init__(message)

async def app_exception_handler(request: Request, exc: AppException) -> JSONResponse:
    """
    Map AppException to a structured JSON response.
    Log the error details for debugging.
    """
    logger.error(f"AppException: {exc.message} | Path: {request.url.path}")
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "error": {
                "type": "AppException",
                "message": exc.message,
            },
        },  
    )


async def generic_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """
    Map unexpected exceptions into HTTP 500.
    Keep the response generic; log details server-side.
    """
    logger.error(f"Unhandled Exception: {str(exc)} | Path: {request.url.path}")
    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "error": {
                "type": "InternalServerError",
                "message": "Internal server error. Please try again later.",
            },
        },  
    )