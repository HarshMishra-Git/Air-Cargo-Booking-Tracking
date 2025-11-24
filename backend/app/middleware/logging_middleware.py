import time
import uuid
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from app.core.logging import get_logger

logger = get_logger(__name__)


class LoggingMiddleware(BaseHTTPMiddleware):
    """Middleware for request/response logging"""
    
    async def dispatch(self, request: Request, call_next):
        # Generate request ID
        request_id = str(uuid.uuid4())
        request.state.request_id = request_id
        
        # Log request
        start_time = time.time()
        logger.info(
            f"Request started | {request.method} {request.url.path} | "
            f"Request-ID: {request_id} | Client: {request.client.host if request.client else 'unknown'}"
        )
        
        try:
            # Process request
            response = await call_next(request)
            
            # Calculate duration
            duration = time.time() - start_time
            
            # Log response
            logger.info(
                f"Request completed | {request.method} {request.url.path} | "
                f"Status: {response.status_code} | Duration: {duration:.3f}s | "
                f"Request-ID: {request_id}"
            )
            
            # Add request ID to response headers
            response.headers["X-Request-ID"] = request_id
            
            return response
        
        except Exception as e:
            # Calculate duration
            duration = time.time() - start_time
            
            # Log error
            logger.error(
                f"Request failed | {request.method} {request.url.path} | "
                f"Error: {str(e)} | Duration: {duration:.3f}s | "
                f"Request-ID: {request_id}"
            )
            raise