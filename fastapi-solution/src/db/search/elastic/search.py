from typing import Any, Iterator

from db.search.abc.query import AbstractQuery
from db.search.abc.search import AbstractSearch
from elasticsearch import AsyncElasticsearch, NotFoundError
from elasticsearch.helpers import async_scan
from aioretry import retry

from db.backoff_policy import retry_policy


class Search(AbstractSearch):
    def __init__(self, hosts) -> None:
        self.hosts = hosts
        return super().__init__()

    @property
    def client(self):
        return AsyncElasticsearch(
            hosts=self.hosts,
            verify_certs=False,
        )

    async def exist(self):
        return

    def batch(
        self,
        items: Iterator[Any],
        size: int,
    ) -> Iterator[Any]:
        """Chunk items on batches."""
        # TODO: заменить на chunk
        collection = []

        while True:
            item = next(items, None)
            collection.append(item)

            if len(collection) >= size or not item:
                yield collection
                collection = []

                if not item:
                    break

        return iter(())

    @retry(retry_policy)
    async def get(
        self,
        index: str,
        id: str | None = None,
    ):
        """Return index data by a query from Elasticsearch."""
        try:
            if not id:
                return None

            doc = await self.client.get(
                index=index,
                id=id,
            )
            return doc.body["_source"]
        except NotFoundError:
            return None

    async def scan(
        self,
        index: str | list[str],
        query: AbstractQuery | None = None,
        scroll: str = "5m",
    ):
        _query = None
        if query:
            _query = query.get_query()
        return async_scan(
            client=self.client,
            index=index,
            query=_query,
            scroll=scroll,
        )

    @retry(retry_policy)
    async def search(
        self,
        index: str | list[str],
        query: AbstractQuery | None = None,
        size: int | None = None,
        from_: int | None = 0,
    ):
        _query = None
        if query:
            _query = query.get_query()

        return await self.client.search(
            index=index,
            body=_query,  # type: ignore
            size=size,
            from_=from_,
        )

    @retry(retry_policy)
    async def scroll(
        self,
        scroll_id: str,
        scroll: str | None = None,
    ):
        return await self.client.scroll(
            scroll_id=scroll_id,
            scroll=scroll,
        )

    @retry(retry_policy)
    async def save_mapping(
        self,
        mapping: dict[str, Any],
        index: str,
    ) -> None:
        await self.client.indices.create(
            index=index,
            mappings=mapping,
        )

    async def save_data_to_index(self, data: Any, index: str):
        raise NotImplementedError

    async def close(self):
        await self.client.transport.close()
