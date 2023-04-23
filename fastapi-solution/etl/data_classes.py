from dataclasses import dataclass
from datetime import datetime
import uuid


@dataclass(slots=True)
class Filmwork:
    id: str
    imdb_rating: float
    genres: list
    title: str
    description: str
    persons: list


@dataclass(slots=True)
class GenreIds:
    genre_id: uuid.UUID
    modified: datetime


@dataclass(slots=True)
class PersonIds:
    person_id: uuid.UUID
    modified: str


@dataclass(slots=True)
class FilmIds:
    fw_id: uuid.UUID
    modified: datetime


@dataclass(slots=True)
class PgDttmStr:
    dttm_str: str
