from http import HTTPStatus
from typing import Any, List

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from uuid import UUID

from services.person import PersonService, get_person_service
from models.film import Film as _Film

router = APIRouter()


class FilmRoles(BaseModel):
    id: str = Field(alias="uuid")
    roles: List[str] = Field(default_factory=list)

    class Config:
        allow_population_by_field_name = True


class Person(BaseModel):
    id: str = Field(alias="uuid")
    name: str = Field(alias="full_name")
    films: List[FilmRoles] = Field(default_factory=list)

    class Config:
        allow_population_by_field_name = True

    @classmethod
    def get_films_roles(cls, person_name: str, films: List[_Film]) -> List[FilmRoles]:
        films_roles = []
        for film in films:
            roles = []

            a = film.actors
            w = film.writers
            d = film.director
            if a:
                if list(filter(lambda x: True if x.name == person_name else False, a)):
                    roles.append("actor")
            if w:
                if list(filter(lambda x: True if x.name == person_name else False, w)):
                    roles.append("writer")
            if d and person_name in d:
                roles.append("director")

            films_roles.append(FilmRoles(uuid=film.id, roles=roles))

        return films_roles


class Film(BaseModel):
    id: UUID = Field(alias="uuid")
    title: str
    imdb_rating: float

    class Config:
        allow_population_by_field_name = True


# Внедряем PersonService с помощью Depends(get_person_service)
@router.get("/{person_id}/film", response_model=List[Film])
async def person_films(
    person_id: str,
    person_service: PersonService = Depends(get_person_service),
) -> Any:  # List[Person]:
    person = await person_service.get_by_id(person_id)
    if not person:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="Person not found")

    films = await person_service.get_person_films(person_id, person.name)
    if not films:
        # Если жанры не найдены, отдаём 404 статус
        # Желательно пользоваться уже определёнными HTTP-статусами, которые содержат enum
        # Такой код будет более поддерживаемым
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="Films not found")

    # Перекладываем данные из models.Genre в Genre
    # Обратите внимание, что у модели бизнес-логики есть поле description
    # Которое отсутствует в модели ответа API.
    # Если бы использовалась общая модель для бизнес-логики и формирования ответов API
    # вы бы предоставляли клиентам данные, которые им не нужны
    # и, возможно, данные, которые опасно возвращать
    films_resp = [Film.parse_obj(x) for x in films]
    return films_resp


# Внедряем GenreService с помощью Depends(get_genre_service)
@router.get("/{person_id}", response_model=Person)
async def person(
    person_id: str,
    person_service: PersonService = Depends(get_person_service),
) -> Person:
    person = await person_service.get_by_id(person_id)
    if not person:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="Person not found")

    films = await person_service.get_person_films(person_id, person.name)
    if not films:
        # Если фильмы не найдены, отдаём 404 статус
        # Желательно пользоваться уже определёнными HTTP-статусами, которые содержат enum
        # Такой код будет более поддерживаемым
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="Films not found")

    person_resp = Person(
        uuid=person.id,
        full_name=person.name,
        films=Person.get_films_roles(person_name=person.name, films=films),
    )

    return person_resp
