from typing import Any

import pytest
from redis.asyncio import Redis

from tests.functional.settings import genres_settings
from tests.functional.utils.helpers import paginate_list
from tests.functional.utils.test_data_generation import generate_genres


@pytest.mark.asyncio
async def test_retrieve_genres_without_cache(
    main_api_url,
    make_get_request,
    create_es_index,
    es_write_data,
    redis_client: Redis,
):
    await create_es_index(
        index=genres_settings.es_index,
        index_settings=genres_settings.es_index_genres_mapping["settings"],
        index_mappings=genres_settings.es_index_genres_mapping["mappings"],
    )

    genres = generate_genres()
    expected_genres_ids = set([genre['id'] for genre in genres])

    await es_write_data(
        genres,
        genres_settings.es_index,
        genres_settings.es_id_field,
    )

    await redis_client.flushall(True)

    api_endpoint_url = f"{main_api_url}/{genres_settings.api_endpoint_url}"
    response_body, _, response_status = await make_get_request(
        request_path=api_endpoint_url,
        query_payload=None,
    )
    resp_genres_ids = set([genre['uuid'] for genre in response_body])

    assert response_status == 200
    assert len(genres) == len(response_body)
    assert expected_genres_ids == resp_genres_ids


@pytest.mark.asyncio
async def test_retrieve_genres_from_cache(
    main_api_url,
    make_get_request,
    create_es_index,
    es_clear_index,
    es_write_data,
):
    await create_es_index(
        index=genres_settings.es_index,
        index_settings=genres_settings.es_index_genres_mapping["settings"],
        index_mappings=genres_settings.es_index_genres_mapping["mappings"],
    )

    genres = generate_genres()
    expected_genres_ids = set([genre['id'] for genre in genres])

    await es_write_data(
        genres,
        genres_settings.es_index,
        genres_settings.es_id_field,
    )

    api_endpoint_url = f"{main_api_url}/{genres_settings.api_endpoint_url}"

    response_body, _, response_status = await make_get_request(
        request_path=api_endpoint_url,
        query_payload=None,
    )

    await es_clear_index(index=genres_settings.es_index)

    response_body, _, response_status = await make_get_request(
        request_path=api_endpoint_url,
        query_payload=None,
    )

    resp_genres_ids = set([genre['uuid'] for genre in response_body])

    assert response_status == 200
    assert len(genres) == len(response_body)
    assert expected_genres_ids == resp_genres_ids
