from functools import lru_cache

import orjson
from db.search.abc.search import AbstractSearch
from db.search.dependency import get_search
from db.cache.redis.redis import get_redis
from fastapi import Depends
from models.genre import Genre
from redis.asyncio import Redis

# TODO: Replace to settings
GENRE_CACHE_EXPIRE_IN_SECONDS = 60 * 10  # 10 минут


class GenreService:
    """Contain a methods for fetching data from ES or Redis."""

    def __init__(self, redis: Redis, search: AbstractSearch):
        self.redis = redis
        self.search = search

    # Возвращает список всех жанров.
    # Он опционален, так как жанр может отсутствовать в базе
    async def get_all(self) -> list[Genre] | None:
        """Return all genres."""
        # Пытаемся получить данные из кеша, потому что оно работает быстрее
        # TODO: return cache back
        # genres = await self._genres_from_cache()

        genres = None
        if not genres:
            # Если жанра нет в кеше, то ищем его в Elasticsearch
            genres = await self._get_genres_from_search()
            if not genres:
                # Если список отсутствует в Elasticsearch, значит ошибка
                return None
            # Сохраняем жанры в кеш
            await self._put_genres_to_cache(genres)

        return genres

    async def _get_genres_from_search(self) -> list[Genre] | None:
        """Return all genres from elastic."""
        hits = []
        _hits = await self.search.scan(index="genres")
        async for hit in _hits:
            hits.append(hit)

        return [Genre.parse_obj(x["_source"]) for x in hits]

    async def _genres_from_cache(self) -> list[Genre] | None:
        """Return all genres from cache."""
        # Пытаемся получить данные о жанре из кеша, используя команду get
        # https://redis.io/commands/get/
        redis_data = await self.redis.get("genres")
        if not redis_data:
            return None

        # pydantic предоставляет API для создания объекта моделей из json
        genres_json = orjson.loads(redis_data.decode("utf-8"))

        return [Genre.parse_obj(x) for x in genres_json]

    async def _put_genres_to_cache(self, genres: list[Genre]):
        """Save all genres from cache."""
        # Сохраняем данные о жанрах, используя команду set
        # Выставляем время жизни кеша — 10 минут
        # https://redis.io/commands/set/
        # pydantic позволяет сериализовать модель в json
        await self.redis.set(
            name="genres",
            value=orjson.dumps(genres, default=dict),
            ex=GENRE_CACHE_EXPIRE_IN_SECONDS,
        )

    # Возвращает жанр по id.
    # Он опционален, так как жанр может отсутствовать в базе
    async def get_by_id(self, genre_id: str) -> Genre | None:
        """Return a genre by id."""
        # Пытаемся получить данные из кеша, потому что оно работает быстрее
        # genre = await self._genre_from_cache(genre_id)
        # TODO cache
        genre = None
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

    async def _genre_from_cache(self, genre_id: str) -> Genre | None:
        """Return a genre from cache by id."""
        # Пытаемся получить данные о жанре из кеша, используя команду hget
        # https://redis.io/commands/hget/
        redis_data = await self.redis.hget("genre", genre_id)
        if not redis_data:
            return None

        # pydantic предоставляет API для создания объекта моделей из json
        genre_json = orjson.loads(redis_data.decode("utf-8"))
        return Genre.parse_obj(genre_json)

    async def _put_genre_to_cache(self, genre: Genre):
        """Save a genre to cache."""
        await self.redis.hset("genre", str(genre.id), genre.json())
        await self.redis.expire("genre", GENRE_CACHE_EXPIRE_IN_SECONDS)


@lru_cache()
def get_genres_service(
    redis: Redis = Depends(get_redis),
    search: AbstractSearch = Depends(get_search),
) -> GenreService:
    """Use for set the dependency in api route."""
    return GenreService(redis, search)
