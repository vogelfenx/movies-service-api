from typing import Optional

from pydantic import BaseModel

from models.common import ConfigOrjsonMixin, IdMixin


class Genre(IdMixin, BaseModel):
    """
    Genre model class.

    Attributes:
        name (str): The name of the genre.
        description (Optional[str]): The description of the genre, if available.
    """

    name: str
    description: Optional[str]

    class Config(ConfigOrjsonMixin):
        pass
