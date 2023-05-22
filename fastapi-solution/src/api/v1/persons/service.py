from functools import lru_cache

from core.logger import get_logger
from db.cache.helpers import prepare_key_by_args
from db.search.abc.search import AbstractSearch
from db.search.dependency import get_search
from db.cache.dependency import get_cache
from db.cache.abc.cache import AbstractCache
from fastapi import Depends
from models.film import Film
from models.person import Person
from .queries import QueryPersonByIdAndName, QueryPersonByName

ES_BODY_SEARCH = "_source"

logger = get_logger(__name__)


class PersonService:
    """Contain a merhods for fetching data from ES or Redis."""

    def __init__(
        self,
        cache: AbstractCache,
        search: AbstractSearch,
    ):
        self.cache = cache
        self.search = search

    # get_by_id возвращает объект персоны.
    # Он опционален, так как персона может отсутствовать в базе
    async def get_by_id(
        self,
        person_id: str,
    ) -> Person | None:
        """Return a person by id."""
        # Пытаемся получить данные из кеша, потому что оно работает быстрее
        person = await self._get_person_from_cache(person_id)
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
        persons = await self._get_persons_by_key_from_cache(key)
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
            await self._put_persons_by_key_to_cache(
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
        query = QueryPersonByName(name=name)

        _hits = await self.search.search(
            index="persons",
            query=query,
            size=page_size,
            from_=page_number,
        )

        hits = _hits["hits"]["hits"]

        return [Person.parse_obj(x["_source"]) for x in hits]

    async def _get_persons_by_key_from_cache(
        self,
        key: str,
    ) -> list[Person] | None:
        """Return persons by name from cache."""
        cached_persons = await self.cache.get(
            name="person_key",
            key=key,
        )
        if not cached_persons:
            return None

        # pydantic предоставляет API для создания объекта моделей из json
        return [Person.parse_obj(person) for person in cached_persons]

    async def _put_persons_by_key_to_cache(
        self,
        key: str,
        persons: list[Person],
    ):
        """Save a person data to cache."""
        await self.cache.set(
            name="person_key",
            key=key,
            key_value=persons,
        )

    async def _get_person_from_search(
        self,
        person_id: str,
    ) -> Person | None:
        """Get a person from search db."""
        hit = await self.search.get(
            index="persons",
            id=person_id,
        )
        if not hit:
            return None

        type("hit=============================")

        type(hit)
        return Person.parse_obj(hit)

    async def _get_person_from_cache(
        self,
        person_id: str,
    ) -> Person | None:
        """Get a person from cache."""
        cached_person = await self.cache.get(name="person", key=person_id)
        if not cached_person:
            return None

        # pydantic предоставляет API для создания объекта моделей из json
        return Person.parse_obj(cached_person)

    async def _put_person_to_cache(
        self,
        person: Person,
    ):
        """Save a person to cache."""
        # pydantic позволяет сериализовать модель в json
        await self.cache.set(
            name="person",
            key=str(person.id),
            key_value=person,
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
        person_films = await self._get_person_films_from_cache(person_id)
        if not person_films:
            # Если жанра нет в кеше, то ищем его в Elasticsearch
            person_films = await self._get_person_films_from_search(
                person_id=person_id,
                person_name=person_name,
            )
            if not person_films:
                # Если список отсутствует в Elasticsearch, значит ошибка
                return None
            # Сохраняем жанры в кеш
            await self._put_person_films_to_cache(
                person_id=person_id,
                person_films=person_films,
            )

        return person_films

    async def _get_person_films_from_search(
        self,
        person_id: str,
        person_name: str,
    ) -> list[Film] | None:
        """Get a person films data from elasticsearch."""
        query = QueryPersonByIdAndName(
            id=person_id,
            name=person_name,
        )

        hits = []
        _hits = await self.search.scan(
            index="movies",
            query=query,
        )
        async for hit in _hits:
            hits.append(hit["_source"])

        return [Film.parse_obj(x) for x in hits]

    async def _get_person_films_from_cache(
        self,
        person_id: str,
    ) -> list[Film] | None:
        """Get a person films data from cache."""
        cached_person_films = await self.cache.get(
            name="person_films",
            key=person_id,
        )
        if not cached_person_films:
            return None

        # pydantic предоставляет API для создания объекта моделей из json
        return [Film.parse_obj(x) for x in cached_person_films]

    async def _put_person_films_to_cache(
        self,
        person_id: str,
        person_films: list[Film],
    ):
        """Save a film data to cache."""
        await self.cache.set(
            name="person_films",
            key=person_id,
            key_value=person_films,
        )

    async def get_person_data(
        self,
        person_id: str,
        person_name: str,
    ) -> list[Film] | None:
        """Get a person films."""
        # Пытаемся получить данные из кеша, потому что оно работает быстрее
        person_data = await self._get_person_data_from_cache(person_id)
        if not person_data:
            # Если жанра нет в кеше, то ищем его в Elasticsearch
            person_data = await self._get_person_data_from_search(
                person_id=person_id,
                person_name=person_name,
            )
            if not person_data:
                return None

            # Сохраняем жанры в кеш
            await self._put_person_data_to_cache(person_id, person_data)

        return person_data

    async def _get_person_data_from_search(
        self,
        person_id: str,
        person_name: str,
    ) -> list[Film] | None:
        """Return person films by id."""
        query = QueryPersonByIdAndName(
            id=person_id,
            name=person_name,
        )

        hits = []
        _hits = await self.search.scan(
            index="movies",
            query=query,
        )
        async for hit in _hits:
            hits.append(hit["_source"])

        return [Film.parse_obj(x) for x in hits]

    async def _get_person_data_from_cache(
        self,
        person_id: str,
    ) -> list[Film] | None:
        """Return person films by id from cache."""
        cached_person_data = await self.cache.get(
            name="person_data",
            key=person_id,
        )
        if not cached_person_data:
            return None

        return [Film.parse_obj(film) for film in cached_person_data]

    async def _put_person_data_to_cache(
        self,
        person_id: str,
        person_data: list[Film],
    ):
        """Save a person data to cache."""
        await self.cache.set(
            name="person_data",
            key=person_id,
            key_value=person_data,
        )


@lru_cache()
def get_person_service(
    cache: AbstractCache = Depends(get_cache),
    search: AbstractSearch = Depends(get_search),
) -> PersonService:
    """Use for set the dependency in api route."""
    return PersonService(cache, search)
