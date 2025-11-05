from typing import Callable
from fastapi import Request, Response
from redis import asyncio as aioredis
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
            try:
                self.redis = await aioredis.from_url(
                    settings.REDIS_URL, 
                    encoding="utf-8", 
                    decode_responses=True
                )
            except Exception as e:
                print(f"Warning: Redis connection failed: {e}. Rate limiting disabled.")
                self.enabled = False

    async def __call__(self, request: Request, call_next: Callable[[Request], Response]) -> Response:
        if not self.enabled:
            return await call_next(request)

        if not self.redis:
            try:
                await self.init()
            except:
                # If Redis fails, continue without rate limiting
                return await call_next(request)

        try:
            ip = request.client.host if request.client else "unknown"
            path = request.url.path
            key = f"ratelimit:{ip}:{path}:{int(time.time() // self.window)}"

            # Increment counter and set expiry
            current = await self.redis.incr(key)
            if current == 1:
                await self.redis.expire(key, self.window)

            if current > self.max_requests:
                return Response(status_code=429, content="Rate limit exceeded. Try again later.")
        except Exception:
            # If Redis fails, continue without rate limiting
            pass

        return await call_next(request)
