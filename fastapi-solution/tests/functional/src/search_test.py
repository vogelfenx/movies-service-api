from typing import Any

import pytest
from redis.asyncio import Redis

from tests.functional.settings import movies_settings
from tests.functional.utils.helpers import paginate_list
from tests.functional.utils.test_data_generation import generate_films


@pytest.mark.parametrize(
    "query_data, expected_response",
    [
        (
            {"query": "Space X", "page_size": 8, "page_number": 2},
            {"status": 200, "length": 30},
        ),
        (
            {"query": "The World Star", "page_size": 21, "page_number": 1},
            {"status": 200, "length": 30},
        ),
    ],
)
@pytest.mark.asyncio
async def test_search_without_cache(
    main_api_url,
    make_get_request,
    create_es_index,
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
        num_films=30,
        film_title=query_data["query"],
    )

    expected_pagination_result = set(
        [
            row[movies_settings.es_id_field]
            for row in paginate_list(
                data_list=generated_films,
                page_size=query_data["page_size"],
                page=query_data["page_number"],
            )
        ]
    )

    generated_films.extend(
        generate_films(num_films=30, film_title="It's a Wonderful Life")
    )

    await es_write_data(
        generated_films,
        movies_settings.es_index,
        movies_settings.es_id_field,
    )

    await redis_client.flushall(True)

    # url = movies_settings.service_url + '/api/v1/films/search'
    url = main_api_url + "/api/v1/films/search"
    response_body, _, response_status = await make_get_request(
        request_path=url,
        query_payload=query_data,
    )
    await redis_client.flushall(True)

    response_pagination_result = set(
        [row["uuid"] for row in response_body["films"]]
    )

    assert response_status == expected_response["status"]
    assert response_body["films_count"] == expected_response["length"]
    assert len(response_body["films"]) == len(expected_pagination_result)
    assert response_pagination_result == expected_pagination_result


@pytest.mark.parametrize(
    "query_data, expected_response",
    [
        (
            {"query": "Space X", "page_size": 8, "page_number": 2},
            {"status": 200, "length": 30},
        ),
        (
            {"query": "The World Star", "page_size": 21, "page_number": 1},
            {"status": 200, "length": 30},
        ),
    ],
)
@pytest.mark.asyncio
async def test_search_cache(
    main_api_url,
    make_get_request,
    create_es_index,
    es_write_data,
    es_clear_index,
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

    expected_pagination_result = set(
        [
            row[movies_settings.es_id_field]
            for row in paginate_list(
                data_list=generated_films,
                page_size=query_data["page_size"],
                page=query_data["page_number"],
            )
        ]
    )

    await es_write_data(
        generated_films,
        movies_settings.es_index,
        movies_settings.es_id_field,
    )

    # url = movies_settings.service_url + '/api/v1/films/search'
    url = main_api_url + "/api/v1/films/search"
    response_body, _, response_status = await make_get_request(
        request_path=url,
        query_payload=query_data,
    )

    await es_clear_index(index=movies_settings.es_index)

    response_body, _, response_status = await make_get_request(
        request_path=url,
        query_payload=query_data,
    )

    response_pagination_result = set(
        [row["uuid"] for row in response_body["films"]]
    )

    assert response_status == expected_response["status"]
    assert len(response_body["films"]) == len(expected_pagination_result)
    assert response_body["films_count"] == expected_response["length"]
    assert response_pagination_result == expected_pagination_result
