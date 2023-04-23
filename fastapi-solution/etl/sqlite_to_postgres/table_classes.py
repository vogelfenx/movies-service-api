import uuid
from dataclasses import dataclass, asdict
from datetime import datetime


def str_to_dttm(dt_str: str):
    return datetime.strptime(dt_str, '%Y-%m-%d %H:%M:%S.%f+00')


@dataclass
class AbstractTable:

    def get_values(self):
        return list(asdict(self).values())


@dataclass
class FilmWork(AbstractTable):
    id: uuid.UUID
    title: str
    description: str | None
    creation_date: datetime | None
    rating: float | None
    type: str
    created: datetime | None
    modified: datetime | None

    @classmethod
    def custom_row_factory(cls, cursor, row):
        column_list = [column[0] for column in cursor.description]
        named_values = {key: value for key, value in zip(column_list, row)}

        return FilmWork(
            id=uuid.UUID(named_values['id']),
            title=named_values['title'],
            description='' if named_values['description'] is None
            else named_values['description'],
            creation_date=None if named_values['creation_date'] is None
            else str_to_dttm(named_values['creation_date']),
            rating=named_values['rating'],
            type=named_values['type'],
            created=None if named_values['created_at'] is None
            else str_to_dttm(named_values['created_at']),
            modified=datetime.now()
        )


@dataclass
class Genre(AbstractTable):
    id: uuid.UUID
    name: str
    description: str | None
    created: datetime | None
    modified: datetime | None

    @classmethod
    def custom_row_factory(cls, cursor, row):
        column_list = [column[0] for column in cursor.description]
        named_values = {key: value for key, value in zip(column_list, row)}

        return Genre(
            id=uuid.UUID(named_values['id']),
            name=named_values['name'],
            description='' if named_values['description'] is None
            else named_values['description'],
            created=None if named_values['created_at'] is None
            else str_to_dttm(named_values['created_at']),
            modified=datetime.now()
        )


@dataclass
class Person(AbstractTable):
    id: uuid.UUID
    full_name: str
    created: datetime | None
    modified: datetime | None

    @classmethod
    def custom_row_factory(cls, cursor, row):
        column_list = [column[0] for column in cursor.description]
        named_values = {key: value for key, value in zip(column_list, row)}

        return Person(
            id=uuid.UUID(named_values['id']),
            full_name=named_values['full_name'],
            created=None if named_values['created_at'] is None
            else str_to_dttm(named_values['created_at']),
            modified=datetime.now()
        )


@dataclass
class GenreFilmWork(AbstractTable):
    id: uuid.UUID
    film_work_id: uuid.UUID
    genre_id: uuid.UUID
    created: datetime | None

    @classmethod
    def custom_row_factory(cls, cursor, row):
        column_list = [column[0] for column in cursor.description]
        named_values = {key: value for key, value in zip(column_list, row)}

        return GenreFilmWork(
            id=uuid.UUID(named_values['id']),
            genre_id=uuid.UUID(named_values['genre_id']),
            film_work_id=uuid.UUID(named_values['film_work_id']),
            created=None if named_values['created_at'] is None
            else str_to_dttm(named_values['created_at']),
        )


@dataclass
class PersonFilmWork(AbstractTable):
    id: uuid.UUID
    film_work_id: uuid.UUID
    person_id: uuid.UUID
    role: str
    created: datetime | None

    @classmethod
    def custom_row_factory(cls, cursor, row):
        column_list = [column[0] for column in cursor.description]
        named_values = {key: value for key, value in zip(column_list, row)}

        return PersonFilmWork(
            id=uuid.UUID(named_values['id']),
            film_work_id=uuid.UUID(named_values['film_work_id']),
            person_id=uuid.UUID(named_values['person_id']),
            role=named_values['role'],
            created=None if named_values['created_at'] is None
            else str_to_dttm(named_values['created_at']),
        )
