from elasticsearch import AsyncElasticsearch
from core.search import AbstractSearch

db: AbstractSearch | None = None


async def get_search() -> AbstractSearch | None:
    """For dependency."""
    return db
