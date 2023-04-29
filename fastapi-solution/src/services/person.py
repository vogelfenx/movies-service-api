from functools import lru_cache
from typing import List, Optional
from .common import prepare_key_by_args

from elasticsearch import AsyncElasticsearch, NotFoundError
from elasticsearch.helpers import async_scan
from fastapi import Depends
import orjson
from redis.asyncio import Redis

from db.elastic import get_elastic
from db.redis import get_redis
from models.person import Person
from models.film import Film
from .queries.person import person_films_query, person_search_query

PERSON_CACHE_EXPIRE_IN_SECONDS = 60 * 5  # 5 минут


class PersonService:
    def __init__(self, redis: Redis, elastic: AsyncElasticsearch):
        self.redis = redis
        self.elastic = elastic

    # get_by_id возвращает объект персоны.
    # Он опционален, так как персона может отсутствовать в базе
    async def get_by_id(self, person_id: str) -> Optional[Person]:
        # Пытаемся получить данные из кеша, потому что оно работает быстрее
        person = await self._person_from_cache(person_id)
        if not person:
            # Если персоны нет в кеше, то ищем его в Elasticsearch
            person = await self._get_person_from_elastic(person_id)
            if not person:
                # Если он отсутствует в Elasticsearch, то персоны вообще нет в базе
                return None
            # Сохраняем персону в кеш
            await self._put_person_to_cache(person)

        return person

    # get_by_id возвращает объект персоны.
    # Он опционален, так как персона может отсутствовать в базе
    async def get_persons_by_name(
        self, name: str, page_size: int, page_number: int
    ) -> Optional[List[Person]]:
        # Пытаемся получить данные из кеша, потому что оно работает быстрее
        # TODO get redis
        key = prepare_key_by_args(
            name=name, page_size=page_size, page_number=page_number
        )
        persons = await self._persons_by_key_from_cache(key)
        if not persons:
            # Если персоны нет в кеше, то ищем его в Elasticsearch
            persons = await self._get_persons_by_name_from_elastic(
                name=name, page_size=page_size, page_number=page_number
            )
            if not persons:
                # Если он отсутствует в Elasticsearch, то персоны вообще нет в базе
                return None
            # Сохраняем персону в кеш
            await self._put_person_by_key_to_cache(key=key, persons=persons)

        return persons

    async def _get_persons_by_name_from_elastic(
        self, name: str, page_size: int, page_number: int
    ) -> Optional[List[Person]]:
        query = person_search_query(name=name)

        docs = await self.elastic.search(
            index="persons", query=query, size=page_size, from_=page_number
        )

        persons = [Person.parse_obj(x["_source"]) for x in docs["hits"]["hits"]]
        return persons

    async def _persons_by_key_from_cache(
        self, key: str | bytes
    ) -> Optional[List[Person]]:
        # Пытаемся получить данные о персоне из кеша по ключу, используя команду hget
        # https://redis.io/commands/get/
        data = await self.redis.hget("person", key)
        if not data:
            return None

        # pydantic предоставляет удобное API для создания объекта моделей из json
        persons_json = orjson.loads(data.decode("utf-8"))
        persons = [Person.parse_obj(x) for x in persons_json]
        return persons

    async def _put_person_by_key_to_cache(
        self, key: str | bytes, persons: List[Person]
    ):
        # Сохраняем данные о персоне, используя команду set
        # Выставляем время жизни кеша — 5 минут
        # https://redis.io/commands/set/
        # pydantic позволяет сериализовать модель в json

        await self.redis.hset("person_films", key, orjson.dumps(persons, default=dict))
        await self.redis.expire("person_films", PERSON_CACHE_EXPIRE_IN_SECONDS)

    async def _get_person_from_elastic(self, person_id: str) -> Optional[Person]:
        try:
            doc = await self.elastic.get(index="persons", id=person_id)
        except NotFoundError:
            return None

        return Person(**doc["_source"])

    async def _person_from_cache(self, person_id: str) -> Optional[Person]:
        # Пытаемся получить данные о персоне из кеша, используя команду get
        # https://redis.io/commands/get/
        data = await self.redis.hget("person", person_id)
        if not data:
            return None

        # pydantic предоставляет удобное API для создания объекта моделей из json
        person_json = orjson.loads(data.decode("utf-8"))
        person = Person.parse_obj(person_json)

        return person

    async def _put_person_to_cache(self, person: Person):
        # Сохраняем данные о персоне, используя команду set
        # Выставляем время жизни кеша — 5 минут
        # https://redis.io/commands/set/
        # pydantic позволяет сериализовать модель в json
        await self.redis.hset("person", str(person.id), person.json())
        await self.redis.expire("person", PERSON_CACHE_EXPIRE_IN_SECONDS)

    # возвращает список всех жанров. Он опционален, так как жанр может отсутствовать в базе
    async def get_person_films(
        self, person_id: str, person_name: str
    ) -> Optional[List[Film]]:
        # Пытаемся получить данные из кеша, потому что оно работает быстрее
        person_films = await self._person_films_from_cache(person_id)
        if not person_films:
            # Если жанра нет в кеше, то ищем его в Elasticsearch
            person_films = await self._get_person_films_from_elastic(
                person_id, person_name
            )
            if not person_films:
                # Если список отсутствует в Elasticsearch, значит ошибка
                return None
            # Сохраняем жанры в кеш
            await self._put_person_films_to_cache(person_id, person_films)

        return person_films

    async def _get_person_films_from_elastic(
        self, person_id: str, person_name: str
    ) -> Optional[List[Film]]:
        docs = []
        query = person_films_query(id=person_id, name=person_name)

        async for doc in async_scan(client=self.elastic, index="movies", query=query):
            docs.append(doc)

        person_films = [Film.parse_obj(x["_source"]) for x in docs]
        return person_films

    async def _person_films_from_cache(self, person_id: str) -> Optional[List[Film]]:
        # Пытаемся получить данные о персоне из кеша, используя команду hget
        # https://redis.io/commands/hget/
        data = await self.redis.hget("person_films", person_id)
        if not data:
            return None

        # pydantic предоставляет удобное API для создания объекта моделей из json
        person_films_json = orjson.loads(data.decode("utf-8"))
        person_films = [Film.parse_obj(x) for x in person_films_json]
        return person_films

    async def _put_person_films_to_cache(
        self, person_id: str, person_films: List[Film]
    ):
        # Сохраняем данные о фильмах, используя команду hset
        # Выставляем время жизни кеша — 10 минут
        # https://redis.io/commands/hset/
        # pydantic позволяет сериализовать модель в json

        await self.redis.hset(
            "person_films", person_id, orjson.dumps(person_films, default=dict)
        )
        await self.redis.expire("person_films", PERSON_CACHE_EXPIRE_IN_SECONDS)

    # возвращает список всех жанров. Он опционален, так как жанр может отсутствовать в базе
    async def get_person_data(
        self, person_id: str, person_name: str
    ) -> Optional[List[Film]]:
        # Пытаемся получить данные из кеша, потому что оно работает быстрее
        person_data = await self._person_data_from_cache(person_id)
        if not person_data:
            # Если жанра нет в кеше, то ищем его в Elasticsearch
            person_data = await self._get_person_data_from_elastic(
                person_id, person_name
            )
            if not person_data:
                # Если список отсутствует в Elasticsearch, значит ошибка
                return None
            # Сохраняем жанры в кеш
            await self._put_person_data_to_cache(person_id, person_data)

        return person_data

    async def _get_person_data_from_elastic(
        self, person_id: str, person_name: str
    ) -> Optional[List[Film]]:
        docs = []
        query = person_films_query(id=person_id, name=person_name)

        async for doc in async_scan(client=self.elastic, index="movies", query=query):
            docs.append(doc)

        person_data = [Film.parse_obj(x["_source"]) for x in docs]
        return person_data

    async def _person_data_from_cache(self, person_id: str) -> Optional[List[Film]]:
        # Пытаемся получить данные о персоне из кеша, используя команду hget
        # https://redis.io/commands/hget/
        data = await self.redis.hget("person_data", person_id)
        if not data:
            return None

        # pydantic предоставляет удобное API для создания объекта моделей из json
        person_data_json = orjson.loads(data.decode("utf-8"))
        person_data = [Film.parse_obj(x) for x in person_data_json]
        return person_data

    async def _put_person_data_to_cache(self, person_id: str, person_data: List[Film]):
        # Сохраняем данные о фильмах, используя команду hset
        # Выставляем время жизни кеша — 10 минут
        # https://redis.io/commands/hset/
        # pydantic позволяет сериализовать модель в json

        await self.redis.hset(
            "person_data", person_id, orjson.dumps(person_data, default=dict)
        )
        await self.redis.expire("person_data", PERSON_CACHE_EXPIRE_IN_SECONDS)


@lru_cache()
def get_person_service(
    redis: Redis = Depends(get_redis),
    elastic: AsyncElasticsearch = Depends(get_elastic),
) -> PersonService:
    return PersonService(redis, elastic)
