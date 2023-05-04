from models.common import ConfigOrjsonMixin, UUIDMixin
from models.person import Person
from pydantic import BaseModel


class Film(UUIDMixin, BaseModel):
    """
    Film model class.

    Attributes:
        title: Title of the film.
        description: Description of the film, if available.
        imdb_rating: Rating of the film on IMDB. Defaults to 0.
        genre: A list of genres of the film.
        director: A list of directors of the film.
        actors: A list of actors, if available.
        writers: A list of writers, if available.
    """

    title: str
    description: str | None
    imdb_rating: float | None
    genre: list[str | None] = []
    director: list[str | None] = []
    actors: list[Person | None] = []
    writers: list[Person | None] = []

    class Config(ConfigOrjsonMixin):
        """Config for aliasing."""

        allow_population_by_field_name = True
