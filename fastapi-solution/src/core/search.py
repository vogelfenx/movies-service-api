"""Здесь должен быть модуль с абстракцией работы с поисковой базой (elasticsearch)"""


from abc import ABC, abstractmethod, abstractproperty
from dataclasses import dataclass
from ssl import create_default_context
from typing import (
    Any,
    AsyncGenerator,
    AsyncIterable,
    AsyncIterator,
    Iterator,
    Protocol,
)

from core.config import es_conf
from elasticsearch import AsyncElasticsearch
from elasticsearch.helpers import async_scan
from pydantic import BaseModel, Field


class AbstractClient(ABC):
    @abstractproperty
    def client(self):
        ...

    @abstractmethod
    async def close(self):
        raise NotImplementedError


class AbstractIndex(ABC):
    @abstractproperty
    def index_name(self) -> str:
        ...


class AbstractSearch(AbstractClient):
    @abstractmethod
    async def get(
        self,
        index: str | list[str],
        id: str | None = None,
    ) -> AsyncIterable:
        """
        Get data from search db by id.

        Returns:
            Should yield every hit.
        """
        raise NotImplementedError

    @abstractmethod
    async def scan(
        self,
        index: str | list[str],
        query: dict | None = None,
    ) -> Iterator:
        """
        Get data from search db using async scan.

        Returns:
            Should yield every hit.
        """
        raise NotImplementedError

    @abstractmethod
    async def save_data_to_index(self, data: Any, index: str):
        """
        Get data by query.

        Args:
            data: something for save to db.
            index: index name for saving.
        """
        raise NotImplementedError

    @abstractmethod
    async def save_mapping(self, mapping: dict[str, Any], index: str):
        """
        Get data by query.

        Args:
            mapping: index template.
            index: index name for saving.
        """

    @abstractmethod
    async def exist(self, index: str) -> bool:
        """
        Check index in db.

        Args:
            index: index name for saving.
        Returns:
            True if index exists.
        """
        raise NotImplementedError


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

    async def get(
        self,
        index: str | list[str],
        id: str | None = None,
        query: dict | None = None,
    ):
        """
        Return index data by a query from Elasticsearch.
        """

        if id and isinstance(id, str) and isinstance(index, str):
            yield await self.client.get(
                index=index,
                id=id,
            )

    async def scan(
        self,
        index: str | list[str],
        query: dict | None = None,
    ):
        async for hit in async_scan(
            client=self.client,
            index=index,
            query=query,
        ):
            yield hit

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
