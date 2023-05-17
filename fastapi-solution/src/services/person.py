from functools import lru_cache

import orjson
from core.logger import get_logger
from core.search import Search
from db.search import get_search
from db.search import get_search
from db.redis import get_redis
from elasticsearch import NotFoundError
from elasticsearch.helpers import async_scan
from fastapi import Depends
from models.film import Film
from models.person import Person
from redis.asyncio import Redis

from .common import prepare_key_by_args
from .queries.person import person_films_query, person_search_query

PERSON_CACHE_EXPIRE_IN_SECONDS = 60 * 5  # 5 минут
ES_BODY_SEARCH = "_source"

logger = get_logger(__name__)


class PersonService:
    """Contain a merhods for fetching data from ES or Redis."""

    def __init__(
        self,
        redis: Redis,
        search: Search,
    ):
        self.redis = redis
        self.search = search

    # get_by_id возвращает объект персоны.
    # Он опционален, так как персона может отсутствовать в базе
    async def get_by_id(
        self,
        person_id: str,
    ) -> Person | None:
        """Return a person by id."""
        # Пытаемся получить данные из кеша, потому что оно работает быстрее
        person = await self._person_from_cache(person_id)
        print("as")
        print("as")
        print("as")
        if not person:
            # Если персоны нет в кеше, то ищем его в Elasticsearch
            person = await self._get_person_from_search(person_id)
            if not person:
                # Если он отсутствует в ES, то персоны вообще нет в базе
                return None
            # Сохраняем персону в кеш
            await self._put_person_to_cache(person)

        return person

    # get_by_id возвращает объект персоны.
    # Он опционален, так как персона может отсутствовать в базе
    async def get_persons_by_name(
        self,
        name: str,
        page_size: int,
        page_number: int,
    ) -> list[Person] | None:
        """Return a person by id."""
        # Подготавливаем ключ из списка пар ключ-значение
        key = prepare_key_by_args(
            name=name,
            page_size=page_size,
            page_number=page_number,
        )
        persons = await self._persons_by_key_from_cache(key)
        if not persons:
            # Если персоны нет в кеше, то ищем его в Elasticsearch
            persons = await self._get_persons_by_name_from_search(
                name=name,
                page_size=page_size,
                page_number=page_number,
            )
            if not persons:
                # Если он отсутствует в ES, то персоны вообще нет в базе
                return None
            # Сохраняем персону в кеш
            await self._put_person_by_key_to_cache(
                key=key,
                persons=persons,
            )

        return persons

    async def _get_persons_by_name_from_search(
        self,
        name: str,
        page_size: int,
        page_number: int,
    ) -> list[Person] | None:
        """Return persons by name from Elasticsearch."""
        query = person_search_query(name=name)

        docs = await self.search.search(
            index="persons",
            query=query,
            size=page_size,
            from_=page_number,
        )

        return [
            Person.parse_obj(x[ES_BODY_SEARCH]) for x in docs["hits"]["hits"]
        ]

    async def _persons_by_key_from_cache(
        self,
        key: str,
    ) -> list[Person] | None:
        """Return persons by name from cache."""
        # Получение данных о персоне из кеша по ключу, используя команду hget
        # https://redis.io/commands/get/
        redis_data = await self.redis.hget("person_key", key)
        if not redis_data:
            return None

        # pydantic предоставляет API для создания объекта моделей из json
        persons_json = orjson.loads(redis_data.decode("utf-8"))
        return [Person.parse_obj(x) for x in persons_json]

    async def _put_person_by_key_to_cache(
        self,
        key: str,
        persons: list[Person],
    ):
        """Save a person data to cache (uses redis hset)."""
        await self.redis.hset(
            "person_key",
            key,
            orjson.dumps(
                persons,
                default=dict,
            ),
        )
        await self.redis.expire("person_key", PERSON_CACHE_EXPIRE_IN_SECONDS)

    async def _get_person_from_search(
        self,
        person_id: str,
    ) -> Person | None:
        """Get a person from search db."""
        try:
            doc = await self.search.get(
                index="persons",
                id=person_id,
            )
        except NotFoundError:
            return None

        return Person(**doc[ES_BODY_SEARCH])

    async def _person_from_cache(
        self,
        person_id: str,
    ) -> Person | None:
        """Get a person from cache."""
        # Пытаемся получить данные о персоне из кеша, используя команду get
        # https://redis.io/commands/get/
        redis_data = await self.redis.hget(
            "person",
            person_id,
        )
        if not redis_data:
            return None

        # pydantic предоставляет API для создания объекта моделей из json
        person_json = orjson.loads(redis_data.decode("utf-8"))
        return Person.parse_obj(person_json)

    async def _put_person_to_cache(
        self,
        person: Person,
    ):
        """Save a person to cache (uses redis hset)."""
        # pydantic позволяет сериализовать модель в json
        await self.redis.hset(
            "person",
            str(person.id),
            person.json(),
        )
        await self.redis.expire(
            "person",
            PERSON_CACHE_EXPIRE_IN_SECONDS,
        )

    # Возвращает список всех жанров.
    # Он опционален, так как жанр может отсутствовать в базе
    async def get_person_films(
        self,
        person_id: str,
        person_name: str,
    ) -> list[Film] | None:
        """Return person films by id."""
        # Пытаемся получить данные из кеша, потому что оно работает быстрее
        person_films = await self._person_films_from_cache(person_id)
        if not person_films:
            # Если жанра нет в кеше, то ищем его в Elasticsearch
            person_films = await self._get_person_films_from_elastic(
                person_id,
                person_name,
            )
            if not person_films:
                # Если список отсутствует в Elasticsearch, значит ошибка
                return None
            # Сохраняем жанры в кеш
            await self._put_person_films_to_cache(
                person_id,
                person_films,
            )

        return person_films

    async def _get_person_films_from_elastic(
        self,
        person_id: str,
        person_name: str,
    ) -> list[Film] | None:
        """Get a person films data from elasticsearch."""
        docs = []
        query = person_films_query(
            person_id=person_id,
            name=person_name,
        )

        async for doc in async_scan(
            client=self.search,
            index="movies",
            query=query,
        ):
            docs.append(doc)

        return [Film.parse_obj(x[ES_BODY_SEARCH]) for x in docs]

    async def _person_films_from_cache(
        self,
        person_id: str,
    ) -> list[Film] | None:
        """Get a person films data from cache (uses redis hget)."""
        redis_data = await self.redis.hget("person_films", person_id)
        if not redis_data:
            return None

        # pydantic предоставляет API для создания объекта моделей из json
        person_films_json = orjson.loads(redis_data.decode("utf-8"))
        return [Film.parse_obj(x) for x in person_films_json]

    async def _put_person_films_to_cache(
        self,
        person_id: str,
        person_films: list[Film],
    ):
        """Save a film data to cache (uses redis hset)."""
        await self.redis.hset(
            "person_films",
            person_id,
            orjson.dumps(person_films, default=dict),
        )
        await self.redis.expire("person_films", PERSON_CACHE_EXPIRE_IN_SECONDS)

    async def get_person_data(
        self,
        person_id: str,
        person_name: str,
    ) -> list[Film] | None:
        """Get a person films."""
        # Пытаемся получить данные из кеша, потому что оно работает быстрее
        person_data = await self._person_data_from_cache(person_id)
        if not person_data:
            # Если жанра нет в кеше, то ищем его в Elasticsearch
            person_data = await self._get_person_data_from_elastic(
                person_id,
                person_name,
            )
            if not person_data:
                return None

            # Сохраняем жанры в кеш
            await self._put_person_data_to_cache(person_id, person_data)

        return person_data

    async def _get_person_data_from_elastic(
        self,
        person_id: str,
        person_name: str,
    ) -> list[Film] | None:
        """Return person films by id."""
        docs = []
        query = person_films_query(
            person_id=person_id,
            name=person_name,
        )

        async for doc in async_scan(
            client=self.search,
            index="movies",
            query=query,
        ):
            docs.append(doc)

        return [Film.parse_obj(x[ES_BODY_SEARCH]) for x in docs]

    async def _person_data_from_cache(
        self,
        person_id: str,
    ) -> list[Film] | None:
        """Return person films by id from cache."""
        redis_data = await self.redis.hget(
            "person_data",
            person_id,
        )
        if not redis_data:
            return None

        person_data_json = orjson.loads(redis_data.decode("utf-8"))
        return [Film.parse_obj(film) for film in person_data_json]

    async def _put_person_data_to_cache(
        self,
        person_id: str,
        person_data: list[Film],
    ):
        """Save a person data to cache (uses redis hset)."""
        await self.redis.hset(
            "person_data",
            person_id,
            orjson.dumps(person_data, default=dict),
        )
        await self.redis.expire(
            "person_data",
            PERSON_CACHE_EXPIRE_IN_SECONDS,
        )


@lru_cache()
def get_person_service(
    redis: Redis = Depends(get_redis),
    search: Search = Depends(get_search),
) -> PersonService:
    """Use for set the dependency in api route."""
    return PersonService(redis, search)
