import asyncio
import os
from typing import Any

import pytest
import requests
from aiohttp import ClientSession
from elasticsearch import AsyncElasticsearch
from redis.asyncio import Redis
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from tests.functional.settings import base_settings
from tests.functional.utils.helpers import get_es_bulk_query

pytest_plugins = ["docker_compose"]


@pytest.fixture(scope="module")
def docker_compose_file(pytestconfig):
    """Config docker-compose for pytest."""
    return os.path.join(str(pytestconfig.rootdir), "docker-compose.test.yaml")


@pytest.fixture(scope="module")
def main_api_url(module_scoped_container_getter):
    """Wait for the api from fastapi_main_app_main to become responsive"""
    request_session = requests.Session()
    retries = Retry(
        total=1, backoff_factor=3, status_forcelist=[500, 502, 503, 504]
    )
    request_session.mount("http://", HTTPAdapter(max_retries=retries))

    api_url = "{0}:{1}/{2}".format(
        base_settings.service_url,
        base_settings.service_url_port,
        base_settings.api_root_endpoint,
    )

    return api_url


@pytest.fixture(scope="session", name="event_loop")
def fixture_event_loop():
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
async def es_client(session_scoped_container_getter):
    """Elasticsearch client fixture."""
    service = session_scoped_container_getter.get(
        "elasticsearch"
    ).network_info[0]

    es_client = AsyncElasticsearch(
        hosts=[
            {
                "host": "localhost",
                # 'host': service.hostname, # TODO: check it later
                "port": int(service.host_port),
                "scheme": "http",
            }
        ],
    )

    yield es_client
    await es_client.close()


@pytest.fixture(scope="session")
async def aiohttp_session():
    session = ClientSession()
    yield session
    await session.close()


@pytest.fixture(scope="session")
async def redis_client():
    """Elasticsearch client fixture."""

    client = Redis(host="localhost", port=6379)

    yield client
    await client.flushall(True)
    await client.close()


@pytest.fixture
def es_write_data(es_client: AsyncElasticsearch):
    async def inner(data: list[dict], es_index: str, es_id_field: str):
        test_data_query = get_es_bulk_query(
            data,
            es_index,
            es_id_field,
        )

        response = await es_client.bulk(
            operations=test_data_query,
            refresh=True,
        )

        if response["errors"]:
            raise Exception("Ошибка записи данных в Elasticsearch")

    return inner


@pytest.fixture
def es_clear_index(es_client: AsyncElasticsearch):
    async def inner(index: str):
        await es_client.delete_by_query(
            index=index,
            query={"match_all": {}},
        )

    return inner


@pytest.fixture
def create_es_index(es_client: AsyncElasticsearch):
    async def inner(index: str, index_settings: dict, index_mappings: dict):
        if await es_client.indices.exists(index=index):
            await es_client.indices.delete(index=index)

        await es_client.indices.create(
            index=index,
            settings=index_settings,
            mappings=index_mappings,
        )

    return inner


@pytest.fixture
def make_get_request(aiohttp_session: ClientSession):
    async def inner(request_path, query_payload) -> tuple[dict, Any, int]:
        async with aiohttp_session.get(
            request_path, params=query_payload
        ) as response:
            response_body = await response.json()
            response_headers = response.headers
            response_status = response.status
            return response_body, response_headers, response_status

    return inner
