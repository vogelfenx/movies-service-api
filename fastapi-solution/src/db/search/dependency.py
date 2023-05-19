from .abc.search import AbstractSearch

db: AbstractSearch | None = None


async def get_search() -> AbstractSearch | None:
    """For create one connection in app as dependency."""
    return db
