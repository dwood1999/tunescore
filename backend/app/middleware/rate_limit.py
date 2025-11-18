"""
Rate limiting middleware for API endpoints
"""

import time
from collections import defaultdict, deque

from fastapi import HTTPException, Request, Response, status
from starlette.middleware.base import BaseHTTPMiddleware


class RateLimitMiddleware(BaseHTTPMiddleware):
    """
    Rate limiting middleware using sliding window algorithm

    Tracks requests per IP address and enforces rate limits
    """

    def __init__(
        self,
        app,
        calls: int = 60,
        period: int = 60,
        burst: int = 10,
        auth_calls: int = 5,
        auth_period: int = 60,
    ):
        """
        Initialize rate limiter

        Args:
            app: FastAPI application
            calls: Number of calls allowed per period (general endpoints)
            period: Time period in seconds
            burst: Additional burst capacity
            auth_calls: Number of auth calls allowed per period
            auth_period: Auth rate limit period in seconds
        """
        super().__init__(app)
        self.calls = calls
        self.period = period
        self.burst = burst
        self.auth_calls = auth_calls
        self.auth_period = auth_period

        # Storage for request tracking
        self.requests: dict[str, deque[tuple[float, str]]] = defaultdict(deque)

        # Auth endpoints that have stricter limits
        self.auth_endpoints = {
            "/api/v1/auth/login",
            "/api/v1/auth/register",
            "/api/v1/auth/refresh",
        }

    def get_client_ip(self, request: Request) -> str:
        """Get client IP address from request"""
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            return forwarded_for.split(",")[0].strip()

        real_ip = request.headers.get("X-Real-IP")
        if real_ip:
            return real_ip.strip()

        return request.client.host if request.client else "unknown"

    def is_auth_endpoint(self, path: str) -> bool:
        """Check if the path is an authentication endpoint"""
        return path in self.auth_endpoints

    def cleanup_old_requests(
        self, ip: str, current_time: float, is_auth: bool = False
    ) -> None:
        """Remove old requests outside the time window"""
        period = self.auth_period if is_auth else self.period
        cutoff_time = current_time - period

        while self.requests[ip] and self.requests[ip][0][0] < cutoff_time:
            self.requests[ip].popleft()

    def count_requests(self, ip: str, endpoint_type: str) -> int:
        """Count requests for specific endpoint type"""
        return sum(1 for _, req_type in self.requests[ip] if req_type == endpoint_type)

    def is_rate_limited(
        self, ip: str, path: str, current_time: float
    ) -> tuple[bool, str]:
        """Check if request should be rate limited"""
        is_auth = self.is_auth_endpoint(path)

        self.cleanup_old_requests(ip, current_time, is_auth)

        if is_auth:
            auth_count = self.count_requests(ip, "auth")
            if auth_count >= self.auth_calls:
                return (
                    True,
                    f"Auth rate limit exceeded: {auth_count}/{self.auth_calls} per {self.auth_period}s",
                )
        else:
            general_count = self.count_requests(ip, "general")
            if general_count >= self.calls + self.burst:
                return (
                    True,
                    f"Rate limit exceeded: {general_count}/{self.calls + self.burst} per {self.period}s",
                )

        return False, ""

    def add_request(self, ip: str, path: str, current_time: float) -> None:
        """Add request to tracking"""
        endpoint_type = "auth" if self.is_auth_endpoint(path) else "general"
        self.requests[ip].append((current_time, endpoint_type))

    def get_rate_limit_headers(
        self, ip: str, path: str, current_time: float
    ) -> dict[str, str]:
        """Get rate limit headers for response"""
        is_auth = self.is_auth_endpoint(path)
        endpoint_type = "auth" if is_auth else "general"

        if is_auth:
            limit = self.auth_calls
            period = self.auth_period
            remaining = max(0, limit - self.count_requests(ip, endpoint_type))
        else:
            limit = self.calls + self.burst
            period = self.period
            remaining = max(0, limit - self.count_requests(ip, endpoint_type))

        reset_time = int(current_time + period)

        return {
            "X-RateLimit-Limit": str(limit),
            "X-RateLimit-Remaining": str(remaining),
            "X-RateLimit-Reset": str(reset_time),
            "X-RateLimit-Window": str(period),
        }

    async def dispatch(self, request: Request, call_next) -> Response:
        """Process request with rate limiting"""
        current_time = time.time()
        client_ip = self.get_client_ip(request)
        path = request.url.path

        # Skip rate limiting for health checks
        if path in ["/health", "/api/v1/health", "/"]:
            return await call_next(request)

        # Check rate limit
        is_limited, reason = self.is_rate_limited(client_ip, path, current_time)

        if is_limited:
            headers = self.get_rate_limit_headers(client_ip, path, current_time)
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail=f"Rate limit exceeded. {reason}",
                headers=headers,
            )

        # Add request to tracking
        self.add_request(client_ip, path, current_time)

        # Process request
        response = await call_next(request)

        # Add rate limit headers to response
        headers = self.get_rate_limit_headers(client_ip, path, current_time)
        for key, value in headers.items():
            response.headers[key] = value

        return response
