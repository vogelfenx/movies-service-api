import asyncio
from os import getenv

from aioretry import retry
from elasticsearch import AsyncElasticsearch
from utils.backoff_policy import retry_policy
from utils.logger import get_logger

logger = get_logger(__name__)


@retry(retry_policy)
async def wait_for_es(es_client: AsyncElasticsearch):
    """Check elasticsearch is ready to accept connections."""
    logger.info("Ping elasticsearch")

    if await es_client.ping():
        logger.info("Elasticsearch is ready to accept connections")
    else:
        raise Exception

    await es_client.close()


async def main():
    es_host = getenv("ELASTIC_HOST", default="localhost")
    es_port = getenv("ELASTIC_PORT", default=9200)

    es_client = AsyncElasticsearch(
        hosts=f"http://{es_host}:{es_port}",
        verify_certs=False,
    )

    try:
        await wait_for_es(es_client)
    finally:
        await es_client.close()

if __name__ == "__main__":
    asyncio.run(main())
