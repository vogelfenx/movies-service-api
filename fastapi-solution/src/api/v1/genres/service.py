from functools import lru_cache

import orjson
from db.search.abc.search import AbstractSearch
from db.search.dependency import get_search
from db.cache.dependency import get_cache
from db.cache.abc.cache import AbstractCache
from fastapi import Depends
from models.genre import Genre
from redis.asyncio import Redis
from core.config import redis_conf


class GenreService:
    """Contain a methods for fetching data from ES or Redis."""

    def __init__(self, cache: AbstractCache, search: AbstractSearch):
        self.cache = cache
        self.search = search

    # Возвращает список всех жанров.
    # Он опционален, так как жанр может отсутствовать в базе
    async def get_all(self) -> list[Genre] | None:
        """Return all genres."""
        genres = await self._get_genres_from_cache()

        if not genres:
            # Если жанра нет в кеше, то ищем его в Elasticsearch
            genres = await self._get_genres_from_search()
            if not genres:
                # Если список отсутствует в Elasticsearch, значит ошибка
                return None
            await self._put_genres_to_cache(genres)

        return genres

    async def _get_genres_from_search(self) -> list[Genre] | None:
        """Return all genres from elastic."""
        hits = []
        _hits = await self.search.scan(index="genres")
        async for hit in _hits:
            hits.append(hit)

        return [Genre.parse_obj(x["_source"]) for x in hits]

    async def _get_genres_from_cache(self) -> list[Genre] | None:
        """Return all genres from cache."""
        cached_genres = await self.cache.get(
            name="all_genres",
            key="all_genres",
        )
        if not cached_genres:
            return None

        return [Genre.parse_obj(genre) for genre in cached_genres]

    async def _put_genres_to_cache(self, genres: list[Genre]):
        """Save all genres from cache."""
        await self.cache.set(
            name="all_genres",
            key="all_genres",
            key_value=genres,
        )

    # Возвращает жанр по id.
    # Он опционален, так как жанр может отсутствовать в базе
    async def get_by_id(self, genre_id: str) -> Genre | None:
        """Return a genre by id."""
        # Пытаемся получить данные из кеша, потому что оно работает быстрее
        genre = await self._get_genre_from_cache(genre_id)
        if not genre:
            # Если жанра нет в кеше, то ищем его в Elasticsearch
            genre = await self._get_genre_from_search(genre_id)
            if not genre:
                # Если список отсутствует в Elasticsearch, значит ошибка
                return None
            # Сохраняем жанры в кеш
            await self._put_genre_to_cache(genre)

        return genre

    async def _get_genre_from_search(self, genre_id: str) -> Genre | None:
        """Return a genre from elastic by id."""
        doc = await self.search.get(
            index="genres",
            id=genre_id,
        )
        if not doc:
            return None

        return Genre.parse_obj(doc)

    async def _get_genre_from_cache(self, genre_id: str) -> Genre | None:
        """Return a genre from cache by id."""
        cached_genre = await self.cache.get(
            name="genre",
            key=genre_id,
        )
        if not cached_genre:
            return None

        return Genre.parse_obj(cached_genre)

    async def _put_genre_to_cache(self, genre: Genre):
        """Save a genre to cache."""
        await self.cache.set(
            name="genre",
            key=str(genre.id),
            key_value=genre,
        )


@lru_cache()
def get_genres_service(
    cache: AbstractCache = Depends(get_cache),
    search: AbstractSearch = Depends(get_search),
) -> GenreService:
    """Use for set the dependency in api route."""
    return GenreService(cache, search)
