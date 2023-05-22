from abc import ABC, abstractmethod, abstractproperty
from typing import Any


class AbstractClient(ABC):
    """Interface for client."""

    @abstractproperty
    def client(self):
        ...

    @abstractmethod
    async def close(self):
        raise NotImplementedError


class AbstractCache(AbstractClient):
    """Interaface for cache."""

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
        key_value: Any,
        expire_time: int | None = None,
    ):
        """Set named cache by a key."""
        raise NotImplementedError
