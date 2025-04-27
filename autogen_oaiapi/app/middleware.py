
from fastapi import Request
from fastapi.responses import JSONResponse, Response
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
import time
import uuid
import logging

from autogen_oaiapi.base.types import (
    ChatCompletionErrorResponse,
    ChatCompletionErrorDetail,
)

logger = logging.getLogger(__name__)

class RequestContextMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        request_id = request.headers.get("x-request-id", str(uuid.uuid4()))
        request.state.request_id = request_id

        start_time = time.time()
        response = await call_next(request)
        duration = time.time() - start_time

        response.headers["x-request-id"] = request_id
        response.headers["x-process-time"] = f"{duration:.4f}s"

        logger.info(f"[{request_id}] {request.method} {request.url.path} ({duration:.2f}s)")
        return response
    

class APIKeyModelMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        if request.method == "OPTIONS":
            # CORS preflight does not auth test!
            pass
        else:        
            auth_header = request.headers.get("Authorization")
            if not auth_header:
                auth_header = request.headers.get("authorization")  # for lowercase header

            if not auth_header or not auth_header.startswith("Bearer "):
                api_key = "BASE_API_KEY"
                # return JSONResponse(status_code=404, content={"detail": "Authorization header missing or invalid"})
            else: 
                api_key = auth_header[len("Bearer "):]
            
            allowed_models = request.app.state.server.key_manager.get_allow_models(api_key)

            if not allowed_models:
                content = ChatCompletionErrorResponse(
                    error=ChatCompletionErrorDetail(
                        message="Invalid API Key",
                        type="authentication_error",
                        param="api_key",
                        code="invalid_api_key"
                    )
                )
                return JSONResponse(status_code=403, content=content.model_dump(exclude_none=False))
                
            if request.method == "POST":
                body = await request.json()
                requested_model = body.get("model")
                if requested_model:
                    if "*" not in allowed_models and requested_model not in allowed_models:
                        content = ChatCompletionErrorResponse(
                            error=ChatCompletionErrorDetail(
                                message=f"Model '{requested_model}' not allowed for this API Key",
                                type="permission_error",
                                param="model",
                                code="model_not_found"
                            )
                        )
                        return JSONResponse(status_code=403, content=content.model_dump(exclude_none=False))
                else:
                    content = ChatCompletionErrorResponse(
                        error=ChatCompletionErrorDetail(
                            message="Model not specified in request body",
                            type="invalid_request_error",
                            param="model",
                            code="model_not_found"
                        )
                    )
                    return JSONResponse(status_code=400, content=content.model_dump(exclude_none=False))

            request.state.api_key = api_key
        return await call_next(request)