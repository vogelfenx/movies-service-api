from datetime import datetime
from uuid import UUID

from orjson import dumps, loads
from pydantic import BaseModel


def orjson_dumps(v, *, default):
    """Decode bytes to unicode."""
    return dumps(v, default=default).decode()


class ConfigOrjsonMixin:
    """
    Mixin class to configure the orjson library for handling JSON files.

    Attributes:
        json_loads: A function to deserialize JSON data into Python objects.
        json_dumps: A function to serialize Python objects into JSON data.
    """

    json_loads = loads
    json_dumps = orjson_dumps


class IdMixin(BaseModel):
    """
    Mixin class to add an 'id' field to a model.

    Attributes:
        id (UUID): A unique identifier for the model instance.
    """

    id: UUID


class DateMixin(BaseModel):
    """
    Mixin class to add datetime fields to a model.

    Attributes:
        created (datetime): The datetime when the model instance was created.
        modified (datetime): The datetime when the model instance was last modified.
    """

    created: datetime
    modified: datetime
