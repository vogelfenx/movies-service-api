from models.common import ConfigOrjsonMixin, IdMixin
from pydantic import BaseModel


class Genre(IdMixin, BaseModel):
    """Genre model class.

    Attributes:
        name (str): The name of the genre.
        description (Optional[str]): The description of the genre.
    """

    name: str
    description: str | None

    class Config(ConfigOrjsonMixin):
        """Configuration for orjson."""
