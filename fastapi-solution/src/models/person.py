from pydantic import BaseModel

from models.common import ConfigOrjsonMixin, IdMixin


class Person(IdMixin, BaseModel):
    """
    Person model class.

    Attributes:
        name (str): The full name of the person.
    """

    name: str

    class Config(ConfigOrjsonMixin):
        pass
