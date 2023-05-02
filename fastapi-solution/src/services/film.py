from functools import lru_cache
from typing import Iterator
from uuid import UUID

import orjson
from elasticsearch import AsyncElasticsearch, NotFoundError
from fastapi import Depends
from redis.asyncio import Redis

from core.config import fast_api_conf
from core.logger import get_logger
from db.elastic import get_elastic
from db.redis import get_redis
from models.film import Film

from .common import prepare_key_by_args

logger = get_logger(__name__)

FILM_CACHE_EXPIRE_IN_SECONDS = 60 * 5  # 5 минут


class FilmService:
    def __init__(self, redis: Redis, elastic: AsyncElasticsearch):
        self.redis = redis
        self.elastic = elastic

    async def get_films_list(
        self,
        page_size: int,
        page_number: int,
        sort_field: dict[str, dict] | None = None,
        filter_field: dict[str, str] | None = None,
        search_query: str | None = None,
        search_fields: list[str] | None = None
    ) -> tuple[int, Iterator[Film]]:
        """
        Fetches films from Redis cache or Elasticsearch index.

        Args:
            page_size: The list size of the films retrieved per page.
            page_number: The page number to retrieve.
            sort_field: The field to sort the results by.
            filter_field: The field to filter the results by.
            search_query: The phrase to search.

        Returns:
            A tuple containing the total number of films and a list of films.
        """

        # кеш может разниться для различных параметров поиска
        # поэтому сохраняем аргументы в строке, которую будем использовать
        # как ключ

        key = prepare_key_by_args(
            page_size=page_size,
            page_number=page_number,
            sort_field=sort_field,
            filter_field=filter_field,
            search_fields=search_fields,
            search_query=search_query
        )
        logger.info("Search films in cache by key <{0}>".format(key))  # type: ignore

        films_count, films = await self._films_list_from_cache(key)

        if page_number:
            from_index = page_size * (page_number - 1)

        if not films:
            films_count, films = await self._get_films_list_from_elastic(
                query_size=page_size,
                from_index=from_index,
                sort_field=sort_field,
                filter_field=filter_field,
                search_query=search_query,
                search_fields=search_fields,
            )

        await self._put_films_to_cache(key, films_count, films)

        return films_count, films

    async def get_by_id(self, film_id: UUID) -> Film | None:
        """Retrieve a film by ID.

        Args:
            film_id: The ID of the film to retrieve.

        Returns:
            The requested film or None.
        """
        film = await self._film_from_cache(str(film_id))
        if not film:
            film = await self._get_film_from_elastic(film_id)
            if not film:
                return None
            await self._put_film_to_cache(film)

        return film

    async def _get_films_list_from_elastic(
        self,
        query_size: int,
        from_index: int = 0,
        sort_field: dict[str, dict] | None = None,
        filter_field: dict[str, str] | None = None,
        search_query: str | None = None,
        search_fields: list[str] | None = None,
    ) -> tuple[int, Iterator[Film]]:
        """Fetch films from elasticsearch.

        If the requested query size is larger than the maximum query size (MAX_ELASTIC_QUERY_SIZE),
        the query will be paginated using elasticsearch's scrolling functionality,
        to avoid overloading elasticsearch.

        Args:
            query_size: The size of the query to retrieve.
            from_index: The document number to return from.
            sort_field: The field to sort the results by.
            filter_field: The field to filter the results by.
            search_query: The phrase to search.
            search_fields: The fields to search in.

        Returns:
            Total number of documents in the index and list of fetched films.
        """
        max_query_size = fast_api_conf.MAX_ELASTIC_QUERY_SIZE
        paginate_query_request = False

        if query_size > max_query_size:
            paginate_query_request = True
            query_size = max_query_size

        query = {
            "query": {
                "bool": {
                    "must": {
                        "match_all": {},
                    },
                },
            },
            "size": query_size,
            "from": from_index or 0,
        }

        if filter_field:
            query["query"]["bool"]["filter"] = {
                "terms": filter_field,
            }

        if sort_field:
            query["sort"] = [sort_field]

        if search_query and search_fields:
            query["query"]["bool"]["must"] = {
                "multi_match": {
                    "query": search_query,
                    "fields": search_fields,
                    "fuzziness": "AUTO",
                    "operator": "and",
                },
            }

        scroll = None
        if paginate_query_request:
            scroll = "5m"

        response = await self.elastic.search(
            index="movies", body=query, scroll=scroll
        )

        films_count = response["hits"]["total"]["value"]
        hits = response["hits"]["hits"]

        if paginate_query_request:
            scroll_id = response["_scroll_id"]
            films = []
            while hits:
                films.extend([Film(**hit["_source"]) for hit in hits])

                response = await self.elastic.scroll(
                    scroll_id=scroll_id, scroll=scroll
                )
                scroll_id = response["_scroll_id"]
                hits = response["hits"]["hits"]
        else:
            films = [Film(**hit["_source"]) for hit in hits]

        return (films_count, films)

    async def _get_film_from_elastic(self, film_id: UUID) -> Film | None:
        """Fetch a film from elasticsearch by ID.

        Args:
            film_id: The ID of the film to retrieve.

        Returns:
            The requested film.
        """
        try:
            doc = await self.elastic.get(index="movies", id=film_id)
        except NotFoundError:
            return None
        return Film(**doc["_source"])

    async def _film_from_cache(self, film_id: str) -> Film | None:
        """Search for a film in cache by film ID."""
        data = await self.redis.get(film_id)
        if not data:
            return None

        film = Film.parse_raw(data)
        return film

    async def _films_list_from_cache(
        self, args_key: list[str]
    ) -> tuple[int | None, list[Film] | None]:
        """
        Fetch films from cache

        Args:
            args_key: The key for films list to retrieve

        Returns:
            Count of films list items, list of films objects
        """
        data = await self.redis.hget("films", args_key)

        if not data:
            return None, None

        json_data = orjson.loads(data.decode("utf-8"))
        films_count = json_data["count"]
        films = [Film.parse_obj(film) for film in json_data["values"]]

        return films_count, films

    async def _put_film_to_cache(self, film: Film) -> None:
        """
        Put film to cache

        Args:
            Film object
        """
        await self.redis.set(
            str(film.id), film.json(), FILM_CACHE_EXPIRE_IN_SECONDS
        )

    async def _put_films_to_cache(
        self, args_key: str, films_count: int, films: Iterator[Film]
    ) -> None:
        """Put films to cache.

        Args:
            args_key: query args for function get_films_list
            films_count: count of films list, that was fetched
            films: films that was fetched
        """
        data = {"count": films_count, "values": list(films)}
        json_data = orjson.dumps(data, default=dict)

        await self.redis.hset("films", args_key, json_data)
        await self.redis.expire("films", FILM_CACHE_EXPIRE_IN_SECONDS)


@lru_cache()
def get_film_service(
    redis: Redis = Depends(get_redis),
    elastic: AsyncElasticsearch = Depends(get_elastic),
) -> FilmService:
    return FilmService(redis, elastic)
