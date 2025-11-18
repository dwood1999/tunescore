"""
Security headers middleware for TuneScore
Implements production-grade security headers
"""

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """
    Add security headers to all responses

    Headers implemented:
    - Strict-Transport-Security (HSTS)
    - X-Content-Type-Options
    - X-Frame-Options
    - X-XSS-Protection
    - Referrer-Policy
    - Permissions-Policy
    """

    async def dispatch(self, request: Request, call_next) -> Response:
        response = await call_next(request)

        # HSTS - Force HTTPS for 1 year
        response.headers["Strict-Transport-Security"] = (
            "max-age=31536000; includeSubDomains; preload"
        )

        # Prevent MIME type sniffing
        response.headers["X-Content-Type-Options"] = "nosniff"

        # Prevent clickjacking
        response.headers["X-Frame-Options"] = "DENY"

        # Enable XSS filter
        response.headers["X-XSS-Protection"] = "1; mode=block"

        # Control referrer information
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"

        # Disable unnecessary browser features
        response.headers["Permissions-Policy"] = (
            "geolocation=(), microphone=(), camera=(), payment=()"
        )

        # Content Security Policy
        # Allow CDN resources for Swagger UI (docs endpoints)
        is_docs_endpoint = (
            request.url.path.startswith("/api/v1/docs") 
            or request.url.path.startswith("/api/v1/redoc")
        )
        
        if is_docs_endpoint:
            # Relaxed CSP for Swagger UI to allow CDN resources
            csp_directives = [
                "default-src 'self'",
                "script-src 'self' 'unsafe-inline' 'unsafe-eval' https://cdn.jsdelivr.net",
                "style-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net",
                "img-src 'self' data: https:",
                "font-src 'self' data: https://cdn.jsdelivr.net",
                "connect-src 'self' http://localhost:5128 http://127.0.0.1:5128 https://cdn.jsdelivr.net",
                "frame-ancestors 'none'",
                "base-uri 'self'",
                "form-action 'self'",
            ]
        else:
            # Strict CSP for all other endpoints
            csp_directives = [
                "default-src 'self'",
                "script-src 'self' 'unsafe-inline' 'unsafe-eval'",
                "style-src 'self' 'unsafe-inline'",
                "img-src 'self' data: https:",
                "font-src 'self' data:",
                "connect-src 'self' http://localhost:5128 http://127.0.0.1:5128",
                "frame-ancestors 'none'",
                "base-uri 'self'",
                "form-action 'self'",
            ]
        response.headers["Content-Security-Policy"] = "; ".join(csp_directives)

        return response
