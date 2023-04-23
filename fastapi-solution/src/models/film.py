from datetime import date
from typing import List, Optional

from models.common import ConfigOrjsonMixin, IdMixin
from models.genre import Genre
from models.person import Person
from pydantic import BaseModel
from pydantic.error_wrappers import ValidationError


class Film(IdMixin, BaseModel):
    """
    Film model class.

    Attributes:
        title (str): Title of the film.
        description (Optional[str]): Description of the film, if available.
        creation_date (Optional[date]): Date when the film was created, if available.
        imdb_rating (float, optional): Rating of the film on IMDB. Defaults to 0.
        genre (List[Genre]): A list of genres of the film.
        director (Person): Director of the film.
        actors (Optional[List[Person]]): A list of actors, if available.
        writers (Optional[List[Person]]): A list of writers, if available.
        actors_names (Optional[List[str]]): A list of names of the actors, if available.
        writers_names (Optional[List[str]]): A list of names of the writers, if available.
    """

    title: str
    description: Optional[str]
    creation_date: Optional[date]
    imdb_rating: float = 0
    genre: List[str]
    director: List[str]
    actors: Optional[List[Person]]
    writers: Optional[List[Person]]
    actors_names: Optional[List[str]]
    writers_names: Optional[List[str]]

    class Config(ConfigOrjsonMixin):
        pass


if __name__ == '__main__':
    json_objects = [
        {
            'id': '63c1b466-e602-4775-bbc8-c91d781fcd6f',
            'title': 'some film title',
            'description': 'some film description',
            'imdb_rating': '5.2',
            'genre': [
                {
                    'id': '63c1b466-e602-4775-bbc8-c91d781fcd6f',
                    'name': 'some genre name',
                    'description': 'some genre description',
                },
            ],
            'director': {
                'id': '63c1b466-e602-4775-bbc8-c91d781fcd6f',
                'full_name': 'Person name',
            },
            'actors': [
                {
                    'id': '63c1b466-e602-4775-bbc8-c91d781fcd6f',
                    'full_name': 'Actor1 name',
                },
                {
                    'id': '63c1b466-e602-4775-bbc8-c91d781fcd6f',
                    'full_name': 'Actor2 name',
                },
            ],
            'writers': [
                {
                    'id': '63c1b466-e602-4775-bbc8-c91d781fcd6f',
                    'full_name': 'Writer1 name',
                },
                {
                    'id': '63c1b466-e602-4775-bbc8-c91d781fcd6f',
                    'full_name': 'Writer2 name',
                },
            ],
            'actors_names': ['Actor1', 'Actor2'],
            'writers_names': ['Writer1', 'Writer2'],
        },
    ]

    for obj in json_objects:
        try:
            film = Film(**obj)
            print('json to Python:\n', film.dict())
            print('Python to json:\n', film.json())
        except ValidationError as error:
            print(error.errors())
