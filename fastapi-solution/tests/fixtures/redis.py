import pytest
from redis.asyncio import Redis


@pytest.fixture(scope="session")
async def redis_client(session_scoped_container_getter):
    """Elasticsearch client fixture."""

    service = session_scoped_container_getter.get("redis").network_info[0]
    client = Redis(
        host="localhost",
        port=int(service.host_port),
    )

    yield client
    await client.flushall(True)
    await client.close()
