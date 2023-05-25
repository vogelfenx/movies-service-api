import uuid
from http import HTTPStatus
from typing import Any

import pytest
from redis.asyncio import Redis
from tests.functional.settings import genres_settings
from tests.functional.utils.test_data_generation import generate_genres

# All test coroutines will be treated as marked.
pytestmark = pytest.mark.asyncio


@pytest.mark.parametrize(
    "use_cache, test_empty_response, expected_status_code",
    [
        (False, True, HTTPStatus.NOT_FOUND),
        (True, False, HTTPStatus.OK),
        (False, False, HTTPStatus.OK),
    ],
)
async def test_retrieve_genres(
    main_api_url,
    make_get_request,
    create_es_index,
    es_write_data,
    es_clean_index,
    redis_client: Redis,
    use_cache: bool,
    test_empty_response: bool,
    expected_status_code: int,
):
    """Test retrieve all genres.

    Use the use_cache flag to test fetching from the cache.
    Provide test_empty_response parameter to test for non-existence.
    """

    await create_es_index(
        index=genres_settings.es_index,
        index_settings=genres_settings.es_index_genres_mapping["settings"],
        index_mappings=genres_settings.es_index_genres_mapping["mappings"],
    )

    if not test_empty_response:
        genres = generate_genres()
        expected_genres_ids = {genre["id"] for genre in genres}
        await es_write_data(
            genres,
            genres_settings.es_index,
            genres_settings.es_id_field,
        )

    api_endpoint_url = f"{main_api_url}/{genres_settings.api_endpoint_url}"

    await redis_client.flushall(True)
    response_body, _, response_status = await make_get_request(
        request_path=api_endpoint_url,
        query_payload=None,
    )

    if use_cache:
        await es_clean_index(index=genres_settings.es_index)
        response_body, _, response_status = await make_get_request(
            request_path=api_endpoint_url,
            query_payload=None,
        )

    assert response_status == expected_status_code
    if response_status == HTTPStatus.OK:
        resp_genres_ids = {genre["uuid"] for genre in response_body}
        assert len(genres) == len(response_body)
        assert expected_genres_ids == resp_genres_ids


@pytest.mark.parametrize(
    "genre, expected_response, use_cache",
    [
        ({"id": uuid.uuid4()}, {"status": HTTPStatus.NOT_FOUND}, False),
        ({"id": uuid.uuid4()}, {"status": HTTPStatus.NOT_FOUND}, True),
        ({"id": "some_string"}, {"status": HTTPStatus.UNPROCESSABLE_ENTITY}, False),
        ({"id": 5}, {"status": HTTPStatus.UNPROCESSABLE_ENTITY}, False),
        (None, {"status": HTTPStatus.OK}, False),
        (None, {"status": HTTPStatus.OK}, True),
    ],
)
async def test_retrieve_genre(
    main_api_url,
    make_get_request,
    create_es_index,
    es_write_data,
    es_clean_index,
    redis_client: Redis,
    genre: dict[str, Any],
    expected_response: dict[str, Any],
    use_cache: bool,
):
    """Test retrieve genre.

    Use the use_cache flag to test fetching from the cache.
    Provide a genre parameter to test for non-existence.
    """
    await create_es_index(
        index=genres_settings.es_index,
        index_settings=genres_settings.es_index_genres_mapping["settings"],
        index_mappings=genres_settings.es_index_genres_mapping["mappings"],
    )

    genres = generate_genres()
    if not genre:
        genre = genres[0]

    await es_write_data(
        genres,
        genres_settings.es_index,
        genres_settings.es_id_field,
    )

    api_endpoint_url = "{base_url}/{endpoint}/{id}".format(
        base_url=main_api_url,
        endpoint=genres_settings.api_endpoint_url,
        id=genre["id"],
    )

    await redis_client.flushall()
    response_body, _, response_status = await make_get_request(
        request_path=api_endpoint_url,
        query_payload=None,
    )

    if use_cache:
        await es_clean_index(index=genres_settings.es_index)
        response_body, _, response_status = await make_get_request(
            request_path=api_endpoint_url,
            query_payload=None,
        )

    assert response_status == expected_response["status"]
    if not genre:
        assert response_body["uuid"] == genre["id"]
