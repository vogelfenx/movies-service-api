import asyncio
from typing import Any

import pytest
import requests
from aiohttp import ClientSession
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from tests.functional.settings import base_settings

pytest_plugins = [
    "tests.fixtures.docker",
    "tests.fixtures.elasticsearch",
    "tests.fixtures.redis",
]


@pytest.fixture(scope="module")
def main_api_url(module_scoped_container_getter):
    """Wait for the api from fastapi_main_app_main to become responsive."""
    request_session = requests.Session()
    retries = Retry(
        total=1,
        backoff_factor=3,
        status_forcelist=[500, 502, 503, 504],
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
async def aiohttp_session():
    session = ClientSession()
    yield session
    await session.close()


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
