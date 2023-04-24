from typing import List, Optional

from pydantic import BaseModel

from models.common import ConfigOrjsonMixin, IdMixin
from models.person import Person


class Film(IdMixin, BaseModel):
    """
    Film model class.

    Attributes:
        title (str): Title of the film.
        description (Optional[str]): Description of the film, if available.
        imdb_rating (float, optional): Rating of the film on IMDB. Defaults to 0.
        genre (Optional[List[Genre]]): A list of genres of the film.
        director (Optional[List[str]]): A list of directors of the film.
        actors (Optional[List[Person]]): A list of actors, if available.
        writers (Optional[List[Person]]): A list of writers, if available.
    """

    title: str
    description: Optional[str]
    imdb_rating: float = 0
    genre: Optional[List[str]]
    director: Optional[List[str]]
    actors: Optional[List[Person]]
    writers: Optional[List[Person]]

    class Config(ConfigOrjsonMixin):
        pass
