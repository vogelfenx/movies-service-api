from typing import Any

import orjson
from redis.asyncio import Redis

from db.cache.abc.cache import AbstractCache


class RedisCache(AbstractCache):
    def __init__(self, host: str, port: int) -> None:
        self.host = host
        self.port = port
        return super().__init__()

    @property
    def client(self):
        return Redis(
            host=self.host,
            port=self.port,
        )

    async def close(self):
        await self.client.close()

    async def get(self, name: str, key: str):
        bytes_value = await self.client.hget(name=name, key=key)
        return orjson.loads(bytes_value.decode("utf-8"))

    async def set(self, name: str, key: str, value: Any):
        bytes_data = orjson.dumps(value, default=dict)

        await self.client.hset(
            name=name,
            key=key,
            value=bytes_data,
        )
