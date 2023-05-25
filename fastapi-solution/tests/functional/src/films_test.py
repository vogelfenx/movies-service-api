import asyncio
from http import HTTPStatus
from typing import Any

import pytest
from redis.asyncio import Redis
from tests.functional.settings import movies_settings
from tests.functional.testdata.film import some_film
from tests.functional.utils.test_data_generation import generate_films

# All test coroutines will be treated as marked.
pytestmark = pytest.mark.asyncio


@pytest.mark.parametrize(
    "query_data, expected_response",
    [
        (
            {"query": "Spam", "film_id": some_film["id"]},
            {"status": HTTPStatus.OK, "title": some_film["title"]},
        ),
        (
            {
                "query": "Egg",
                "film_id": "1de4d9aa-9ff6-4b1e-b54f-06c6f28cbd2a",
            },
            {"status": HTTPStatus.NOT_FOUND, "title": some_film["title"]},
        ),
        (
            {"query": "Foo", "film_id": "some_string"},
            {
                "status": HTTPStatus.UNPROCESSABLE_ENTITY,
                "title": some_film["title"],
            },
        ),
        (
            {"query": "Foo", "film_id": 5},
            {
                "status": HTTPStatus.UNPROCESSABLE_ENTITY,
                "title": some_film["title"],
            },
        ),
    ],
)
async def test_find_specified_films_without_cache(
    main_api_url,
    create_es_index,
    make_get_request,
    es_write_data,
    redis_client: Redis,
    query_data: dict[str, Any],
    expected_response: dict[str, Any],
):
    await create_es_index(
        index=movies_settings.es_index,
        index_settings=movies_settings.es_index_movies_mapping["settings"],
        index_mappings=movies_settings.es_index_movies_mapping["mappings"],
    )

    generated_films = generate_films(
        num_films=30, film_title=query_data["query"]
    )

    generated_films.append(some_film)

    await es_write_data(
        generated_films,
        movies_settings.es_index,
        movies_settings.es_id_field,
    )

    await redis_client.flushall(True)

    api_endpoint_url = "{0}/{1}/{2}".format(
        main_api_url,
        movies_settings.api_endpoint_url,
        query_data["film_id"],
    )

    response_body, _, response_status = await make_get_request(
        request_path=api_endpoint_url,
        query_payload=None,
    )
    await redis_client.flushall(True)

    assert response_status == expected_response["status"]
    if "title" in response_body.keys():
        assert response_body["title"] == expected_response["title"]


@pytest.mark.parametrize(
    "query_data, expected_response",
    [
        (
            {
                "query": "Space X",
            },
            {"status": HTTPStatus.OK, "title": some_film["title"]},
        )
    ],
)
async def test_find_specified_films_cache(
    main_api_url,
    create_es_index,
    make_get_request,
    es_write_data,
    es_clean_index,
    query_data: dict[str, Any],
    expected_response: dict[str, Any],
):
    await create_es_index(
        index=movies_settings.es_index,
        index_settings=movies_settings.es_index_movies_mapping["settings"],
        index_mappings=movies_settings.es_index_movies_mapping["mappings"],
    )

    generated_films = generate_films(
        num_films=30, film_title=query_data["query"]
    )

    generated_films.append(some_film)

    await es_write_data(
        generated_films,
        movies_settings.es_index,
        movies_settings.es_id_field,
    )

    api_endpoint_url = "{0}/{1}/{2}".format(
        main_api_url,
        movies_settings.api_endpoint_url,
        some_film["id"],
    )

    response_body, _, response_status = await make_get_request(
        request_path=api_endpoint_url,
        query_payload=query_data,
    )

    await es_clean_index(index=movies_settings.es_index)

    response_body, _, response_status = await make_get_request(
        request_path=api_endpoint_url,
        query_payload=query_data,
    )

    assert response_status == expected_response["status"]
    assert response_body["title"] == expected_response["title"]


@pytest.mark.parametrize(
    "query_data, expected_response",
    [
        (
            {
                "query": "Space X",
            },
            {
                "status": HTTPStatus.OK,
                "films_count": 31,
                "title": some_film["title"],
            },
        )
    ],
)
async def test_find_films_without_cache(
    main_api_url,
    create_es_index,
    make_get_request,
    es_write_data,
    redis_client: Redis,
    query_data: dict[str, Any],
    expected_response: dict[str, Any],
):
    await create_es_index(
        index=movies_settings.es_index,
        index_settings=movies_settings.es_index_movies_mapping["settings"],
        index_mappings=movies_settings.es_index_movies_mapping["mappings"],
    )

    generated_films = generate_films(
        num_films=30, film_title=query_data["query"]
    )

    generated_films.append(some_film)

    await es_write_data(
        generated_films,
        movies_settings.es_index,
        movies_settings.es_id_field,
    )

    await redis_client.flushall(True)

    api_endpoint_url = "{0}/{1}".format(
        main_api_url,
        movies_settings.api_endpoint_url,
    )

    query_data.update(
        {
            "sort": "+imdb_rating",
            "page_size": 10,
            "page_number": 4,
        }
    )

    response_body, _, response_status = await make_get_request(
        request_path=api_endpoint_url,
        query_payload=query_data,
    )
    await redis_client.flushall(True)

    assert response_status == expected_response["status"]
    assert response_body["films_count"] == expected_response["films_count"]
    assert response_body["films"][0]["title"] == expected_response["title"]


@pytest.mark.parametrize(
    "query_data, expected_response",
    [
        (
            {
                "query": "Space X",
            },
            {
                "status": HTTPStatus.OK,
                "films_count": 31,
                "title": some_film["title"],
            },
        )
    ],
)
async def test_find_films_cache(
    main_api_url,
    create_es_index,
    make_get_request,
    es_write_data,
    es_clean_index,
    query_data: dict[str, Any],
    expected_response: dict[str, Any],
):
    await create_es_index(
        index=movies_settings.es_index,
        index_settings=movies_settings.es_index_movies_mapping["settings"],
        index_mappings=movies_settings.es_index_movies_mapping["mappings"],
    )

    generated_films = generate_films(
        num_films=30, film_title=query_data["query"]
    )

    generated_films.append(some_film)

    await es_write_data(
        generated_films,
        movies_settings.es_index,
        movies_settings.es_id_field,
    )

    api_endpoint_url = "{0}/{1}".format(
        main_api_url,
        movies_settings.api_endpoint_url,
    )

    query_data.update(
        {
            "sort": "+imdb_rating",
            "page_size": 10,
            "page_number": 4,
        }
    )

    response_body, _, response_status = await make_get_request(
        request_path=api_endpoint_url,
        query_payload=query_data,
    )

    await es_clean_index(index=movies_settings.es_index)

    response_body, _, response_status = await make_get_request(
        request_path=api_endpoint_url,
        query_payload=query_data,
    )

    assert response_status == expected_response["status"]
    assert response_body["films_count"] == expected_response["films_count"]
    assert response_body["films"][0]["title"] == expected_response["title"]
