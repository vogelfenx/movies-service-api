import pytest
from elasticsearch import AsyncElasticsearch
from tests.functional.utils.helpers import get_es_bulk_query


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
                "port": int(service.host_port),
                "scheme": "http",
            }
        ],
    )

    yield es_client
    await es_client.close()


@pytest.fixture
def es_write_data(es_client: AsyncElasticsearch):
    """Save data into the index."""

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
def es_clean_index(es_client: AsyncElasticsearch):
    """Delete all data in the index."""

    async def inner(index: str):
        await es_client.delete_by_query(
            index=index,
            query={"match_all": {}},
        )

    return inner


@pytest.fixture
def create_es_index(es_client: AsyncElasticsearch):
    """Create index with a defined mapping."""

    async def inner(index: str, index_settings: dict, index_mappings: dict):
        if await es_client.indices.exists(index=index):
            await es_client.indices.delete(index=index)

        await es_client.indices.create(
            index=index,
            settings=index_settings,
            mappings=index_mappings,
        )

    return inner
