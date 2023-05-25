import asyncio
from os import getenv

from aioretry import retry
from redis.asyncio import Redis
from tests.functional.utils.backoff_policy import retry_policy
from tests.functional.utils.logger import get_logger

logger = get_logger(__name__)


@retry(retry_policy)
async def wait_for_redis(redis_client: Redis):
    """Check redis is ready to accept connections."""
    logger.info("Ping redis")

    if await redis_client.ping():
        logger.info("Redis is ready to accept connections")
    else:
        raise Exception


async def main():
    redis_host = getenv("REDIS_HOST", default="localhost")
    redis_port = getenv("REDIS_PORT", default=6379)

    redis_client = Redis(host=redis_host, port=redis_port)

    try:
        await wait_for_redis(redis_client)
    finally:
        await redis_client.close()


if __name__ == "__main__":
    asyncio.run(main())
