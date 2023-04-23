from datetime import date
from typing import List, Optional

from common import ConfigOrjsonMixin, DateMixin, IdMixin
from genre import Genre
from person import Person
from pydantic import BaseModel
from pydantic.error_wrappers import ValidationError


class Film(IdMixin, BaseModel):

    title: str
    description: Optional[str]
    creation_date: Optional[date]
    imdb_rating: float = 0
    genre: List[Genre]
    director: Person
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
