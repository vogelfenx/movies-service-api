from http import HTTPStatus
from typing import List

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from uuid import UUID

from services.person import PersonService, get_person_service
from models.film import Film as _Film
from models.common import UUIDMixin

router = APIRouter()


class FilmRoles(UUIDMixin, BaseModel):
    """Response nested model contains film uuid and roles"""

    roles: List[str] = Field(default_factory=list)

    class Config:
        allow_population_by_field_name = True


class Person(UUIDMixin, BaseModel):
    """Response person model with only specific fields"""

    name: str = Field(alias="full_name")
    films: List[FilmRoles] = Field(default_factory=list)

    class Config:
        allow_population_by_field_name = True

    @classmethod
    def get_films_roles(cls, person_name: str, films: List[_Film]) -> List[FilmRoles]:
        """Extracts roles from films"""
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
    """Response film model with only specific fields"""

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
) -> List[Film]:
    """Return a person's films (only films list)"""

    person = await person_service.get_by_id(person_id)
    if not person:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="Person not found")

    films = await person_service.get_person_films(person_id, person.name)
    if not films:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="Films not found")

    films_resp = [Film.parse_obj(x) for x in films]
    return films_resp


@router.get("/{person_id}", response_model=Person)
async def person(
    person_id: str,
    person_service: PersonService = Depends(get_person_service),
) -> Person:
    """Return a person's films (only uuid) and roles (as a list)"""
    person = await person_service.get_by_id(person_id)
    if not person:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="Person not found")

    films = await person_service.get_person_films(person_id, person.name)
    if not films:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="Films not found")

    person_resp = Person(
        uuid=person.id,
        full_name=person.name,
        films=Person.get_films_roles(person_name=person.name, films=films),
    )

    return person_resp
