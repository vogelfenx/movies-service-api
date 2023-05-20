from typing import Any

import orjson
from redis.asyncio import Redis

from core.logger import get_logger
from db.cache.abc.cache import AbstractCache
from core.config import redis_conf

logger = get_logger(__name__)


class RedisCache(AbstractCache):
    def __init__(self, host: str, port: int) -> None:
        self.host = host
        self.port = port
        self._client = Redis(
            host=self.host,
            port=self.port,
        )
        return super().__init__()

    @property
    def client(self):
        """Ger or initialize Redis Connection."""
        return self._client

    async def close(self):
        """Close Redis connection."""
        await self.client.close()

    async def get(self, name: str, key: str) -> Any | None:
        """Get data from Redis cache using hash name."""
        logger.info(f"Search hash {name} in redis cache by key <{key}>")
        key_value = await self.client.hget(name=name, key=key)
        if isinstance(key_value, bytes):
            key_value = orjson.loads(key_value.decode("utf-8"))
        return key_value

    async def set(
        self,
        name: str,
        key: str,
        key_value: Any,
        expire_time: int = redis_conf.REDIS_EXPIRE,
    ):
        """Set data to Redis cache using hash name."""
        logger.info(f"Put hash {name} in redis cache by key <{key}>")
        if not isinstance(key_value, bytes):
            key_value = orjson.dumps(key_value, default=dict)

        await self.client.hset(
            name=name,
            key=key,
            value=key_value,
        )
        await self.client.expire(
            name=name,
            time=expire_time,
        )
