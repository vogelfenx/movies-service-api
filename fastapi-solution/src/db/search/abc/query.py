from typing import TypeVar

from .model import IndexMixin
from abc import ABC, abstractmethod

S = TypeVar("S", bound=IndexMixin)


class AbstractQuery(ABC):
    """Abstraction for query."""

    @abstractmethod
    def get_query(self) -> dict:
        raise NotImplementedError


class SelectQuery(AbstractQuery):
    """Combine query and field in one query."""

    @property
    def query(self) -> dict:
        raise NotImplementedError

    @property
    def fields(self) -> list[str] | None:
        raise NotImplementedError

    def get_query(self) -> dict:
        query = self.query.copy()
        if self.fields:
            query["_source"] = self.fields
        return query
