from typing import Callable
from fastapi import Request, Response
import time
import httpx

from app.config import settings

class RateLimiter:
    def __init__(self):
        self.enabled = settings.RATE_LIMIT_ENABLED
        self.window = settings.RATE_LIMIT_WINDOW_SECONDS
        self.max_requests = settings.RATE_LIMIT_MAX_REQUESTS
        self.use_upstash = bool(settings.UPSTASH_REDIS_REST_URL and settings.UPSTASH_REDIS_REST_TOKEN)
        self.redis = None

    async def init(self):
        # Upstash REST API doesn't need init, just use HTTP client
        if self.use_upstash:
            return
        
        # Fallback to direct Redis connection
        if self.enabled and not self.redis:
            try:
                from redis import asyncio as aioredis
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

        # Use Upstash REST API if configured
        if self.use_upstash:
            try:
                ip = request.client.host if request.client else "unknown"
                path = request.url.path
                key = f"ratelimit:{ip}:{path}:{int(time.time() // self.window)}"
                
                async with httpx.AsyncClient() as client:
                    # Increment counter
                    incr_response = await client.post(
                        f"{settings.UPSTASH_REDIS_REST_URL}/incr/{key}",
                        headers={"Authorization": f"Bearer {settings.UPSTASH_REDIS_REST_TOKEN}"}
                    )
                    
                    if incr_response.status_code == 200:
                        result = incr_response.json()
                        current = result.get("result", 0)
                        
                        # Set expiry on first request
                        if current == 1:
                            await client.post(
                                f"{settings.UPSTASH_REDIS_REST_URL}/expire/{key}/{self.window}",
                                headers={"Authorization": f"Bearer {settings.UPSTASH_REDIS_REST_TOKEN}"}
                            )
                        
                        if current > self.max_requests:
                            return Response(status_code=429, content="Rate limit exceeded. Try again later.")
            except Exception as e:
                # If Upstash fails, continue without rate limiting
                print(f"Upstash rate limit error: {e}")
                pass
        else:
            # Fallback to direct Redis
            if not self.redis:
                try:
                    await self.init()
                except:
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
                pass

        return await call_next(request)
