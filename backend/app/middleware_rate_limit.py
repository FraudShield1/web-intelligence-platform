from typing import Callable
from fastapi import Request, Response
import aioredis
import time

from app.config import settings

class RateLimiter:
    def __init__(self):
        self.enabled = settings.RATE_LIMIT_ENABLED
        self.window = settings.RATE_LIMIT_WINDOW_SECONDS
        self.max_requests = settings.RATE_LIMIT_MAX_REQUESTS
        self.redis = None

    async def init(self):
        if self.enabled and not self.redis:
            self.redis = await aioredis.from_url(settings.REDIS_URL, encoding="utf-8", decode_responses=True)

    async def __call__(self, request: Request, call_next: Callable[[Request], Response]) -> Response:
        if not self.enabled:
            return await call_next(request)

        if not self.redis:
            await self.init()

        ip = request.client.host if request.client else "unknown"
        path = request.url.path
        key = f"ratelimit:{ip}:{path}:{int(time.time() // self.window)}"

        # Increment counter and set expiry
        current = await self.redis.incr(key)
        if current == 1:
            await self.redis.expire(key, self.window)

        if current > self.max_requests:
            return Response(status_code=429, content="Rate limit exceeded. Try again later.")

        return await call_next(request)
