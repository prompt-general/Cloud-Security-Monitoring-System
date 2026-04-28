import os
import redis


def get_redis_client() -> redis.Redis:
    host = os.getenv("REDIS_HOST", "redis")
    port = int(os.getenv("REDIS_PORT", "6379"))
    db = int(os.getenv("REDIS_DB", "0"))
    return redis.Redis(host=host, port=port, db=db, decode_responses=True)


def cache_baseline(client: redis.Redis, user_id: str, baseline: dict) -> None:
    key = f"baseline:{user_id}"
    client.hset(key, mapping=baseline)
    client.expire(key, 86400)


def get_cached_baseline(client: redis.Redis, user_id: str) -> dict | None:
    key = f"baseline:{user_id}"
    return client.hgetall(key) if client.exists(key) else None
