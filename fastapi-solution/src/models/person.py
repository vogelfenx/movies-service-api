from models.common import ConfigOrjsonMixin, IdMixin
from pydantic import BaseModel


class Person(IdMixin, BaseModel):
    """Person model class.

    Attributes:
        name (str): The full name of the person.
    """

    name: str

    class Config(ConfigOrjsonMixin):
        """Configuration for orjson."""
