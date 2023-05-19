from uuid import uuid4
from random import uniform as random_uniform


def generate_films(
        num_films: int,
        film_title: str,
        genres: list[str] | None = None
) -> list[dict]:
    if not genres:
        genres = ['Action', 'Sci-Fi']

    films = []
    for _ in range(num_films):
        film = {
            'id': str(uuid4()),
            'imdb_rating': round(random_uniform(0, 10), 1),
            'genre': genres,
            'title': film_title,
            'description': 'New World',
            'director': ['Stan'],
            'actors_names': ['Ann', 'Bob'],
            'writers_names': ['Ben', 'Howard'],
            'actors': [
                {'id': str(uuid4()), 'name': 'Ann'},
                {'id': str(uuid4()), 'name': 'Bob'}
            ],
            'writers': [
                {'id': str(uuid4()), 'name': 'Ben'},
                {'id': str(uuid4()), 'name': 'Howard'}
            ]
        }
        films.append(film)

    return films


def generate_persons(
        num_persons: int,
        person_name: str,
) -> list[dict]:

    persons = []

    for _ in range(num_persons):
        person = {
            'id': str(uuid4()),
            'name': person_name
        }
        persons.append(person)

    return persons


def generate_films_by_person(
        num_films: int,
        film_title: str,
        person_id: str,
        person_name: str,
        genres: list[str] | None = None
) -> list[dict]:
    if not genres:
        genres = ['Action', 'Sci-Fi']

    films = []
    for _ in range(num_films):
        film = {
            'id': str(uuid4()),
            'imdb_rating': round(random_uniform(0, 10), 1),
            'genre': genres,
            'title': film_title,
            'description': 'New World',
            'director': ['Stan'],
            'actors_names': ['Ann', person_name],
            'writers_names': ['Ben', 'Howard'],
            'actors': [
                {'id': person_id, 'name': person_name},
                {'id': str(uuid4()), 'name': 'Bob'}
            ],
            'writers': [
                {'id': str(uuid4()), 'name': 'Ben'},
                {'id': str(uuid4()), 'name': 'Howard'}
            ]
        }
        films.append(film)

    return films