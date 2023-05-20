from abc import ABC, abstractmethod, abstractproperty
from typing import Any


class AbstractClient(ABC):
    @abstractproperty
    def client(self):
        ...

    @abstractmethod
    async def close(self):
        raise NotImplementedError


class AbstractCache(AbstractClient):
    @abstractmethod
    async def get(
        self,
        name: str,
        key: str,
    ):
        """Get named cache by a key."""
        raise NotImplementedError

    @abstractmethod
    async def set(
        self,
        name: str,
        key: str,
        value: dict,
    ):
        """Set named cache by a key."""
        raise NotImplementedError
