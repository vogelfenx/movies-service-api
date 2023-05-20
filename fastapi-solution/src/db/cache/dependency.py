from db.cache.abc.cache import AbstractCache

cache: AbstractCache | None = None


async def get_cache() -> AbstractCache | None:
    """For create one connection in app as dependency."""
    return cache
