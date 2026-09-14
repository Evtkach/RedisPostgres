from redis import asyncio as aioredis
from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend

async def init_redis():
    # Подключение к локальному Redis
    redis = aioredis.from_url("redis://localhost:6379", encoding="utf8", decode_responses=True)
    # Инициализация глобального кэша
    FastAPICache.init(RedisBackend(redis), prefix="fastapi-cache")
