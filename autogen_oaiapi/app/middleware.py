
from starlette.middleware.base import BaseHTTPMiddleware
import time
import uuid
import logging

logger = logging.getLogger(__name__)

class RequestContextMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        request_id = request.headers.get("x-request-id", str(uuid.uuid4()))
        request.state.request_id = request_id

        start_time = time.time()
        response = await call_next(request)
        duration = time.time() - start_time

        response.headers["x-request-id"] = request_id
        response.headers["x-process-time"] = f"{duration:.4f}s"

        logger.info(f"[{request_id}] {request.method} {request.url.path} ({duration:.2f}s)")
        return response