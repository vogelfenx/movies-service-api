from typing import Optional

from common import ConfigOrjsonMixin, DateMixin, IdMixin
from pydantic import BaseModel
from pydantic.error_wrappers import ValidationError


class Genre(DateMixin, IdMixin, BaseModel):
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


if __name__ == '__main__':
    json_objects = [
        {
            'id': '63c1b466-e602-4775-bbc8-c91d781fcd6f',
            'name': 'some genre name',
            'description': 'some genre description',
            'created': '2022-05-01 12:30',
            'modified': '2022-10-01 13:30',
        },
        {
            'id': '63c1b466-e602-4775-bbc8-c91d781fcd6f',
            'name': 'some genre name',
            'created': '2022-05-01 12:30',
            'modified': '2022-10-01 13:30',
        },
        {
            'id': '63c1b466-e602-4775-bbc8-c91d781fcd6',
            'name': 'invalid uuid',
            'description': 'some genre description',
            'created': '2022-05-01 12:30',
            'modified': '2022-10-01 13:30',
        },
    ]

    for obj in json_objects:
        try:
            genre = Genre(**obj)
            print('json to Python:\n', genre.dict())
            print('Python to json:\n', genre.json())
        except ValidationError as error:
            print(error.errors())
