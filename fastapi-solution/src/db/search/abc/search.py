"""Здесь должен быть модуль с абстракцией работы с поисковой базой (elasticsearch)"""
from abc import ABC, abstractmethod, abstractproperty
from typing import Any

from .query import AbstractQuery


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
        index: str,
        id: str | None = None,
    ):
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
        query: AbstractQuery | None = None,
        scroll: str = "5m",
    ):
        """
        Get data from search db using async scan.
        Using scroll.

        Returns:
            Should yield every hit.
        """
        raise NotImplementedError

    @abstractmethod
    async def search(
        self,
        index: str | list[str],
        query: AbstractQuery | None = None,
        size: int | None = None,
        from_: int | None = None,
    ):
        """
        Get data from search db using async scan.
        Using pagination.

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
