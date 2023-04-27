from functools import lru_cache
from typing import Dict, Iterator, Optional, Tuple

from elasticsearch import AsyncElasticsearch, BadRequestError, NotFoundError
from fastapi import Depends, HTTPException
from redis.asyncio import Redis

from core import config
from core.logger import LOGGING
from db.elastic import get_elastic
from db.redis import get_redis
from models.film import Film

FILM_CACHE_EXPIRE_IN_SECONDS = 60 * 5  # 5 минут


class FilmService:
    def __init__(self, redis: Redis, elastic: AsyncElasticsearch):
        self.redis = redis
        self.elastic = elastic

    async def get_films_list(
        self,
        page_size: Optional[int],
        page_number: Optional[int],
        sort_field: Optional[str],
        filter_field: Optional[Tuple[str, str]],
    ) -> Tuple[int, Iterator[Film]]:
        """
        Fetches films from Redis cache or Elasticsearch index.

        Args:
            page_size (Optional[int]): The list size of the films retrieved per page.
            page_number (Optional[int]): The page number to retrieve.
            sort_field (Optional[str]): The field to sort the results by.
            filter_field (Optional[Tuple[str, str]]): The field to filter the results by.

        Returns:
            Tuple[int, Iterator[Film]]: A tuple containing the total number of films
              and a list of films.

        Raises:
            HTTPException: If an error occurs while fetching films from Elasticsearch.
        """
        films_count, films = await self._films_list_from_cache()  # TODO redis

        if page_number:
            from_index = page_size * (page_number - 1)

        if not films:
            try:
                films_count, films = await self._get_films_list_from_elastic(
                    query_size=page_size,
                    from_index=from_index,
                    sort_field=sort_field,
                    filter_field=filter_field,
                )
            except BadRequestError as error:
                raise HTTPException(status_code=error.status_code)

        # await self._put_films_to_cache(films) # TODO redis

        return films_count, films

    async def get_by_id(self, film_id: str) -> Optional[Film]:
        """Retrieve a film by ID.

        Args:
            film_id (str): The ID of the film to retrieve.

        Returns:
            Optional[Film]: The retrieved film.
        """
        # TODO redis: Пытаемся получить данные из кеша, потому что оно работает быстрее
        film = await self._film_from_cache(film_id)
        if not film:
            film = await self._get_film_from_elastic(film_id)
            if not film:
                return None
            # TODO redis: Сохраняем фильм  в кеш
            await self._put_film_to_cache(film)

        return film

    async def _get_films_list_from_elastic(
        self,
        query_size: Optional[int],
        from_index: Optional[int],
        sort_field: Optional[Dict[str, str]] = None,
        filter_field: Optional[Tuple[str, str]] = None,
    ) -> Tuple[int, Iterator[Film]]:
        """Fetch films from elasticsearch.

        If the requested query size is larger than the maximum query size (MAX_ELASTIC_QUERY_SIZE),
        the query will be paginated using elasticsearch's scrolling functionality,
        to avoid overloading elasticsearch.

        Args:
            query_size (Optional [int]): The size of the query to retrieve.
            from_index (Optional[int]): The document number to return from.

        Returns:
            Tuple[int, Iterator[Film]]: Total number of documents in the index
                                        and list of fetched films.
        """
        max_query_size = config.MAX_ELASTIC_QUERY_SIZE
        paginate_query_request = False

        if query_size > max_query_size:
            paginate_query_request = True
            query_size = max_query_size

        search_query = {
            'query': {
                'bool': {
                    'must': {
                        'match_all': {},
                    },
                },
            },
            'size': query_size,
            'from': from_index or 0,
        }

        if filter_field:
            search_query['query']['bool']['filter'] = {
                'terms': filter_field,
            }

        if sort_field:
            search_query['sort'] = [sort_field]

        scroll = None
        if paginate_query_request:
            scroll = '5m'

        response = await self.elastic.search(index='movies', body=search_query, scroll=scroll)

        films_count = response['hits']['total']['value']
        hits = response['hits']['hits']

        if paginate_query_request:
            scroll_id = response['_scroll_id']
            films = []
            while hits:
                films.extend([Film(**hit['_source']) for hit in hits])

                response = await self.elastic.scroll(scroll_id=scroll_id, scroll=scroll)
                scroll_id = response['_scroll_id']
                hits = response['hits']['hits']
        else:
            films = (Film(**hit['_source']) for hit in hits)

        return (films_count, films)

    async def _get_film_from_elastic(self, film_id: str) -> Optional[Film]:
        """Fetch a film from elasticsearch by ID.

        Args:
            film_id (str): The ID of the film to retrieve.

        Returns:
            Optional[Film]: The retrieved film.
        """
        try:
            doc = await self.elastic.get(index='movies', id=film_id)
        except NotFoundError:
            return None
        return Film(**doc['_source'])

    async def _film_from_cache(self, film_id: str) -> Optional[Film]:
        # TODO redis: Пытаемся получить данные о фильме из кеша, используя команду get
        # https://redis.io/commands/get/
        data = await self.redis.get(film_id)
        if not data:
            return None

        film = Film.parse_raw(data)
        return film

    async def _films_list_from_cache(self) -> Optional[Film]:
        # TODO redis: Redis Implementation
        return None, None

    async def _put_film_to_cache(self, film: Film):
        # TODO redis: Сохраняем данные о фильме, используя команду set
        # Выставляем время жизни кеша — 5 минут
        # https://redis.io/commands/set/
        # pydantic позволяет сериализовать модель в json
        await self.redis.set(film.id, film.json(), FILM_CACHE_EXPIRE_IN_SECONDS)


@lru_cache()
def get_film_service(
    redis: Redis = Depends(get_redis),
    elastic: AsyncElasticsearch = Depends(get_elastic),
) -> FilmService:
    return FilmService(redis, elastic)
