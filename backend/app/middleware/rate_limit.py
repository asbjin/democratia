# DemocratIA - Rate limiting middleware

import time
from collections import defaultdict

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse

MAX_REQUESTS = 100
WINDOW_SECONDS = 60


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Sliding window rate limiter by client IP."""

    def __init__(self, app):
        super().__init__(app)
        self._requests: dict[str, list[float]] = defaultdict(list)

    def _get_client_ip(self, request: Request) -> str:
        forwarded = request.headers.get("x-forwarded-for")
        if forwarded:
            return forwarded.split(",")[0].strip()
        return request.client.host if request.client else "unknown"

    def _clean_old_requests(self, ip: str, now: float) -> None:
        cutoff = now - WINDOW_SECONDS
        self._requests[ip] = [t for t in self._requests[ip] if t > cutoff]

    async def dispatch(self, request: Request, call_next):
        # Skip rate limiting for health checks
        if request.url.path == "/api/health":
            return await call_next(request)

        ip = self._get_client_ip(request)
        now = time.time()

        self._clean_old_requests(ip, now)

        if len(self._requests[ip]) >= MAX_REQUESTS:
            return JSONResponse(
                status_code=429,
                content={
                    "detail": "Trop de requetes. Limite : 100 par minute.",
                    "retry_after": WINDOW_SECONDS,
                },
            )

        self._requests[ip].append(now)
        response = await call_next(request)
        return response
