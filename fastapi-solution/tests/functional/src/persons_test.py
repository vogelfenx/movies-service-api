from typing import Any

import pytest
from redis.asyncio import Redis

from tests.functional.settings import persons_settings, movies_settings
from tests.functional.utils.test_data_generation import generate_films, generate_persons, generate_films_by_person
from tests.functional.testdata.person import some_person


@pytest.mark.parametrize(
    'query_data, expected_response',
    [
        (
            {
                'person_name': 'Morpheus',
            },
            {'status': 200, 'name': some_person['name'], 'uuid': some_person['id']}
        )
    ]
)
@pytest.mark.asyncio
async def test_find_person_without_cache(
    main_api_url,
    create_es_index,
    make_get_request,
    es_write_data,
    redis_client: Redis,
    query_data: dict[str, Any],
    expected_response: dict[str, Any]
):

    await create_es_index(
        index=persons_settings.es_index,
        index_settings=persons_settings.es_index_movies_mapping['settings'],
        index_mappings=persons_settings.es_index_movies_mapping['mappings']
    )

    generated_persons = generate_persons(num_persons=30,
                                         person_name=query_data['person_name'])

    generated_persons.append(some_person)

    await es_write_data(
        generated_persons,
        persons_settings.es_index,
        persons_settings.es_id_field,
    )

    await redis_client.flushall(True)

    api_endpoint_url = "{0}/{1}/{2}".format(
        main_api_url,
        persons_settings.api_endpoint_url,
        some_person['id'],
    )

    response_body, _, response_status = await make_get_request(
        request_path=api_endpoint_url,
        query_payload=query_data,
    )

    await redis_client.flushall(True)

    assert response_status == expected_response['status']
    assert response_body['full_name'] == expected_response['name']
    assert response_body['uuid'] == expected_response['uuid']


@pytest.mark.parametrize(
    'query_data, expected_response',
    [
        (
            {
                'person_name': 'Morpheus',
            },
            {'status': 200, 'name': some_person['name'], 'uuid': some_person['id']}
        )
    ]
)
@pytest.mark.asyncio
async def test_find_person_cache(
    main_api_url,
    create_es_index,
    make_get_request,
    es_write_data,
    es_clear_index,
    query_data: dict[str, Any],
    expected_response: dict[str, Any]
):

    await create_es_index(
        index=persons_settings.es_index,
        index_settings=persons_settings.es_index_movies_mapping['settings'],
        index_mappings=persons_settings.es_index_movies_mapping['mappings']
    )

    generated_persons = generate_persons(num_persons=30,
                                         person_name=query_data['person_name'])

    generated_persons.append(some_person)

    await es_write_data(
        generated_persons,
        persons_settings.es_index,
        persons_settings.es_id_field,
    )

    api_endpoint_url = "{0}/{1}/{2}".format(
        main_api_url,
        persons_settings.api_endpoint_url,
        some_person['id'],
    )

    response_body, _, response_status = await make_get_request(
        request_path=api_endpoint_url,
        query_payload=query_data,
    )

    await es_clear_index(index=persons_settings.es_index)

    response_body, _, response_status = await make_get_request(
        request_path=api_endpoint_url,
        query_payload=query_data,
    )

    assert response_status == expected_response['status']
    assert response_body['full_name'] == expected_response['name']
    assert response_body['uuid'] == expected_response['uuid']


@pytest.mark.parametrize(
    'query_data, expected_response',
    [
        (
            {
                'title': 'Matrix'
            },
            {'status': 200, 'films_count': 30}
        )
    ]
)
@pytest.mark.asyncio
async def test_find_person_films_without_cache(
    main_api_url,
    create_es_index,
    make_get_request,
    es_write_data,
    redis_client: Redis,
    query_data: dict[str, Any],
    expected_response: dict[str, Any]
):
    await create_es_index(
        index=persons_settings.es_index,
        index_settings=persons_settings.es_index_movies_mapping['settings'],
        index_mappings=persons_settings.es_index_movies_mapping['mappings']
    )

    await create_es_index(
        index=movies_settings.es_index,
        index_settings=movies_settings.es_index_movies_mapping['settings'],
        index_mappings=movies_settings.es_index_movies_mapping['mappings']
    )

    generated_films = generate_films_by_person(num_films=30,
                                               film_title=query_data['title'],
                                               person_id=some_person['id'],
                                               person_name=some_person['name'])

    await es_write_data(
        generated_films,
        movies_settings.es_index,
        movies_settings.es_id_field,
    )

    await es_write_data(
        [some_person],
        persons_settings.es_index,
        persons_settings.es_id_field
    )

    await redis_client.flushall(True)

    api_endpoint_url = "{0}/{1}/{2}/film".format(
        main_api_url,
        persons_settings.api_endpoint_url,
        some_person['id'],
    )

    response_body, _, response_status = await make_get_request(
        request_path=api_endpoint_url,
        query_payload=query_data,
    )

    await redis_client.flushall(True)

    assert response_status == expected_response['status']
    assert len(response_body) == expected_response['films_count']


@pytest.mark.parametrize(
    'query_data, expected_response',
    [
        (
            {
                'title': 'Matrix'
            },
            {'status': 200, 'films_count': 30}
        )
    ]
)
@pytest.mark.asyncio
async def test_find_person_films_cache(
    main_api_url,
    create_es_index,
    make_get_request,
    es_write_data,
    es_clear_index,
    query_data: dict[str, Any],
    expected_response: dict[str, Any]
):
    await create_es_index(
        index=persons_settings.es_index,
        index_settings=persons_settings.es_index_movies_mapping['settings'],
        index_mappings=persons_settings.es_index_movies_mapping['mappings']
    )

    await create_es_index(
        index=movies_settings.es_index,
        index_settings=movies_settings.es_index_movies_mapping['settings'],
        index_mappings=movies_settings.es_index_movies_mapping['mappings']
    )

    generated_films = generate_films_by_person(num_films=30,
                                               film_title=query_data['title'],
                                               person_id=some_person['id'],
                                               person_name=some_person['name'])

    await es_write_data(
        generated_films,
        movies_settings.es_index,
        movies_settings.es_id_field,
    )

    await es_write_data(
        [some_person],
        persons_settings.es_index,
        persons_settings.es_id_field
    )

    api_endpoint_url = "{0}/{1}/{2}/film".format(
        main_api_url,
        persons_settings.api_endpoint_url,
        some_person['id'],
    )

    response_body, _, response_status = await make_get_request(
        request_path=api_endpoint_url,
        query_payload=query_data,
    )

    await es_clear_index(index=movies_settings.es_index)
    await es_clear_index(index=persons_settings.es_index)

    response_body, _, response_status = await make_get_request(
        request_path=api_endpoint_url,
        query_payload=query_data,
    )

    assert response_status == expected_response['status']
    assert len(response_body) == expected_response['films_count']


@pytest.mark.parametrize(
    'query_data, expected_response',
    [
        (
            {
                'title': 'Matrix'
            },
            {'status': 200,
             'films_count': 30,
             'person_id': some_person['id'],
             'person_name': some_person['name']
             }
        )
    ]
)
@pytest.mark.asyncio
async def test_search_person_without_cache(
    main_api_url,
    create_es_index,
    make_get_request,
    es_write_data,
    redis_client: Redis,
    query_data: dict[str, Any],
    expected_response: dict[str, Any]
):
    await create_es_index(
        index=persons_settings.es_index,
        index_settings=persons_settings.es_index_movies_mapping['settings'],
        index_mappings=persons_settings.es_index_movies_mapping['mappings']
    )

    await create_es_index(
        index=movies_settings.es_index,
        index_settings=movies_settings.es_index_movies_mapping['settings'],
        index_mappings=movies_settings.es_index_movies_mapping['mappings']
    )

    generated_films = generate_films_by_person(num_films=30,
                                               film_title=query_data['title'],
                                               person_id=some_person['id'],
                                               person_name=some_person['name'])

    generated_films.extend(generate_films(
            num_films=20,
            film_title='Mandolorian'
    ))

    await es_write_data(
        generated_films,
        movies_settings.es_index,
        movies_settings.es_id_field,
    )

    await es_write_data(
        [some_person],
        persons_settings.es_index,
        persons_settings.es_id_field
    )

    await redis_client.flushall(True)

    api_endpoint_url = "{0}/{1}/search".format(
        main_api_url,
        persons_settings.api_endpoint_url,
    )
    query_data["query"] = some_person['name']

    response_body, _, response_status = await make_get_request(
        request_path=api_endpoint_url,
        query_payload=query_data,
    )

    await redis_client.flushall(True)

    assert response_status == expected_response['status']
    assert len(response_body[0]['films']) == expected_response['films_count']
    assert response_body[0]['uuid'] == expected_response['person_id']
    assert response_body[0]['full_name'] == expected_response['person_name']


@pytest.mark.parametrize(
    'query_data, expected_response',
    [
        (
            {
                'title': 'Matrix'
            },
            {'status': 200,
             'films_count': 30,
             'person_id': some_person['id'],
             'person_name': some_person['name']
             }
        )
    ]
)
@pytest.mark.asyncio
async def test_search_person_cache(
    main_api_url,
    create_es_index,
    make_get_request,
    es_write_data,
    es_clear_index,
    query_data: dict[str, Any],
    expected_response: dict[str, Any]
):
    await create_es_index(
        index=persons_settings.es_index,
        index_settings=persons_settings.es_index_movies_mapping['settings'],
        index_mappings=persons_settings.es_index_movies_mapping['mappings']
    )

    await create_es_index(
        index=movies_settings.es_index,
        index_settings=movies_settings.es_index_movies_mapping['settings'],
        index_mappings=movies_settings.es_index_movies_mapping['mappings']
    )

    generated_films = generate_films_by_person(num_films=30,
                                               film_title=query_data['title'],
                                               person_id=some_person['id'],
                                               person_name=some_person['name'])

    generated_films.extend(generate_films(
            num_films=20,
            film_title='Mandolorian'
    ))

    await es_write_data(
        generated_films,
        movies_settings.es_index,
        movies_settings.es_id_field,
    )

    await es_write_data(
        [some_person],
        persons_settings.es_index,
        persons_settings.es_id_field
    )

    # url = main_api_url + '/api/v1/persons/search?query=' + some_person['name']
    api_endpoint_url = "{0}/{1}/search".format(
        main_api_url,
        persons_settings.api_endpoint_url,
    )
    query_data["query"] = some_person['name']

    response_body, _, response_status = await make_get_request(
        request_path=api_endpoint_url,
        query_payload=query_data,
    )

    await es_clear_index(index=movies_settings.es_index)
    await es_clear_index(index=persons_settings.es_index)

    response_body, _, response_status = await make_get_request(
        request_path=api_endpoint_url,
        query_payload=query_data,
    )

    assert response_status == expected_response['status']
    assert len(response_body[0]['films']) == expected_response['films_count']
    assert response_body[0]['uuid'] == expected_response['person_id']
    assert response_body[0]['full_name'] == expected_response['person_name']
