from redis.asyncio import Redis

from app.core.config import get_settings

redis_client: Redis = Redis.from_url(get_settings().redis_url, decode_responses=True)


async def get_redis() -> Redis:
    """FastAPI dependency: shared Redis client (it manages its own connection pool)."""
    return redis_client
