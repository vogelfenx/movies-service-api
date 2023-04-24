from functools import lru_cache
from typing import List, Optional

from elasticsearch import AsyncElasticsearch, NotFoundError
from fastapi import Depends
import orjson
from redis.asyncio import Redis

from db.elastic import get_elastic
from db.redis import get_redis
from models.genre import Genre

GENRE_CACHE_EXPIRE_IN_SECONDS = 60 * 10  # 10 минут


class GenreService:
    def __init__(self, redis: Redis, elastic: AsyncElasticsearch):
        self.redis = redis
        self.elastic = elastic

    # возвращает список всех жанров. Он опционален, так как жанр может отсутствовать в базе
    async def get_all(self) -> Optional[List[Genre]]:
        # Пытаемся получить данные из кеша, потому что оно работает быстрее
        genres = await self._genres_from_cache()
        if not genres:
            # Если жанра нет в кеше, то ищем его в Elasticsearch
            es = await self._get_genres_from_elastic()
            if not genres:
                # Если список отсутствует в Elasticsearch, значит ошибка
                return None
            # Сохраняем жанры в кеш
            await self._put_genres_to_cache(genres)

        return genres

    async def _get_genres_from_elastic(self) -> Optional[List[Genre]]:
        docs = await self.elastic.search(index="genres")
        genres = [Genre.parse_obj(x["_source"]) for x in docs.body["hits"]["hits"]]
        return genres

    async def _genres_from_cache(self) -> Optional[List[Genre]]:
        # Пытаемся получить данные о жанре из кеша, используя команду get
        # https://redis.io/commands/get/
        data = await self.redis.get("genres")
        if not data:
            return None

        # pydantic предоставляет удобное API для создания объекта моделей из json
        genres_json = orjson.loads(data.decode("utf-8"))
        genres = [Genre.parse_obj(x) for x in genres_json]
        return genres

    async def _put_genres_to_cache(self, genres: List[Genre]):
        # Сохраняем данные о жанре, используя команду set
        # Выставляем время жизни кеша — 10 минут
        # https://redis.io/commands/set/
        # pydantic позволяет сериализовать модель в json
        await self.redis.set(
            name="genres",
            value=orjson.dumps(genres, default=dict),
            ex=GENRE_CACHE_EXPIRE_IN_SECONDS,
        )


@lru_cache()
def get_genres_service(
    redis: Redis = Depends(get_redis),
    elastic: AsyncElasticsearch = Depends(get_elastic),
) -> GenreService:
    return GenreService(redis, elastic)
