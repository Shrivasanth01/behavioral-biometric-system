import time
import asyncio
from collections import defaultdict
from typing import Dict, List, Tuple
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from app.config import settings
from app.exceptions import RateLimitException


class RateLimiter:
    def __init__(self):
        self._windows: Dict[str, List[float]] = defaultdict(list)
        self._lock = asyncio.Lock()

    async def check(self, key: str, max_requests: int, window_seconds: int) -> bool:
        now = time.time()
        async with self._lock:
            window_start = now - window_seconds
            self._windows[key] = [t for t in self._windows[key] if t > window_start]
            if len(self._windows[key]) >= max_requests:
                return False
            self._windows[key].append(now)
        return True

    def get_remaining(self, key: str, max_requests: int, window_seconds: int) -> int:
        now = time.time()
        window_start = now - window_seconds
        if key in self._windows:
            valid = [t for t in self._windows[key] if t > window_start]
            return max(0, max_requests - len(valid))
        return max_requests


rate_limiter = RateLimiter()


class RateLimitMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        if not settings.RATE_LIMIT_ENABLED or request.method == "OPTIONS":
            return await call_next(request)

        path = request.url.path
        user_key = f"ip:{request.client.host}" if request.client else "unknown"

        if path.startswith("/api/auth"):
            max_req = settings.RATE_LIMIT_AUTH_ENDPOINTS
            window = settings.RATE_LIMIT_AUTH_WINDOW
        else:
            max_req = settings.RATE_LIMIT_DEFAULT
            window = settings.RATE_LIMIT_WINDOW

        allowed = await rate_limiter.check(user_key, max_req, window)
        if not allowed:
            raise RateLimitException(f"Rate limit exceeded. Try again in {window}s")

        response = await call_next(request)
        remaining = rate_limiter.get_remaining(user_key, max_req, window)
        response.headers["X-RateLimit-Limit"] = str(max_req)
        response.headers["X-RateLimit-Remaining"] = str(remaining)
        response.headers["X-RateLimit-Reset"] = str(int(time.time()) + window)
        return response
