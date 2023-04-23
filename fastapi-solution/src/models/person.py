from typing import Optional

from common import ConfigOrjsonMixin, IdMixin
from pydantic import BaseModel
from pydantic.error_wrappers import ValidationError


class Person(IdMixin, BaseModel):
    """
    Person model class.

    Attributes:
        full_name (str): The full name of the person.
        gender (Optional[str]): The gender of the person, if available.
    """

    full_name: str
    gender: Optional[str]

    class Config(ConfigOrjsonMixin):
        pass


if __name__ == '__main__':
    json_objects = [
        {
            'id': '63c1b466-e602-4775-bbc8-c91d781fcd6f',
            'full_name': 'Person name',
            'gender': 'male',
        },
        {
            'id': '63c1b466-e602-4775-bbc8-c91d781fcd6f',
            'full_name': 'Person name',
        },
        {
            'id': '63c1b466',
            'full_name': 'invalid uuid',
            'gender': 'male',
        },
    ]

    for obj in json_objects:
        try:
            genre = Person(**obj)
            print('json to Python:\n', genre.dict())
            print('Python to json:\n', genre.json())
        except ValidationError as error:
            print(error.errors())
