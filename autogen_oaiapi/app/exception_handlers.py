from fastapi import Request, FastAPI
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
import logging

logger = logging.getLogger(__name__)

async def http_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    if not isinstance(exc, StarletteHTTPException):
        raise TypeError(f"Exception must be of type StarletteHTTPException but got {type(exc)}")
    logger.warning(f"HTTPException: {exc.detail} (status code: {exc.status_code})")
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": "HTTPException", "detail": exc.detail},
    )

async def validation_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    if not isinstance(exc, RequestValidationError):
        raise TypeError(f"Exception must be of type RequestValidationError but got {type(exc)}")
    logger.warning(f"Validation error: {exc.errors()}")
    return JSONResponse(
        status_code=422,
        content={"error": "ValidationError", "detail": exc.errors()},
    )

async def generic_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    logger.error(f"Unhandled exception: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"error": "InternalServerError", "detail": "An unexpected error occurred."},
    )

def register_exception_handlers(app: FastAPI) -> None:
    """Register custom exception handlers for the FastAPI application."""
    app.add_exception_handler(StarletteHTTPException, http_exception_handler)
    app.add_exception_handler(RequestValidationError, validation_exception_handler)
    app.add_exception_handler(Exception, generic_exception_handler)
