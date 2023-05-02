from http import HTTPStatus
from typing import Annotated
from uuid import UUID

from core.config import fast_api_conf
from fastapi import APIRouter, Depends, HTTPException, Path, Query
from models.common import UUIDMixin
from models.film import Film as _Film
from pydantic import BaseModel, Field
from services.person import PersonService, get_person_service

router = APIRouter()


class FilmRoles(UUIDMixin, BaseModel):
    """Response nested model contains film uuid and roles."""

    roles: list[str] = Field(default_factory=list)

    class Config:
        """Config for aliases."""

        allow_population_by_field_name = True


class Person(UUIDMixin, BaseModel):
    """Response person model with only specific fields."""

    name: str = Field(alias="full_name")
    films: list[FilmRoles] = Field(default_factory=list)

    class Config:
        """Config for aliases."""

        allow_population_by_field_name = True

    @classmethod
    def get_films_roles(
        cls,
        person_name: str,
        films: list[_Film],
    ) -> list[FilmRoles]:
        """Extract roles from films."""
        films_roles = []
        for film in films:
            roles = []

            a = film.actors
            w = film.writers
            d = film.director
            if a:
                if list(
                    filter(
                        lambda x: True
                        if x and x.name == person_name
                        else False,
                        a,
                    ),
                ):
                    roles.append("actor")
            if w:
                if list(
                    filter(
                        lambda x: True
                        if x and x.name == person_name
                        else False,
                        w,
                    ),
                ):
                    roles.append("writer")
            if d and person_name in d:
                roles.append("director")

            films_roles.append(FilmRoles(uuid=film.id, roles=roles))

        return films_roles


class Film(BaseModel):
    """Response film model with only specific fields."""

    id: UUID = Field(alias="uuid")
    title: str
    imdb_rating: float

    class Config:
        """Config for aliases."""

        allow_population_by_field_name = True


@router.get("/search", response_model=list[Person])
async def person_search(
    query: Annotated[
        str,
        Query(
            description="Part of name for search",
            min_length=3,
            max_length=50,
        ),
    ],
    page_size: Annotated[
        int,
        Query(description="Pagination page size", ge=1),
    ] = fast_api_conf.DEFAULT_ELASTIC_QUERY_SIZE,
    page_number: Annotated[
        int,
        Query(description="Number of page", ge=0),
    ] = 0,
    person_service: PersonService = Depends(get_person_service),
) -> list[Person]:
    """Search a person's films by query (part of name).

    Raises:
        HTTPException: If requested person not found.
    """
    person_resp: list[Person] = []
    persons = await person_service.get_persons_by_name(
        name=query,
        page_size=page_size,
        page_number=page_number,
    )
    if not persons:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail="Person not found",
        )

    for person in persons:
        films = await person_service.get_person_films(
            person_id=str(person.id),
            person_name=person.name,
        )
        if films:
            person_resp.append(
                Person(
                    uuid=person.id,
                    full_name=person.name,
                    films=Person.get_films_roles(
                        person_name=person.name,
                        films=films,
                    ),
                ),
            )
        else:
            person_resp.append(
                Person(
                    uuid=person.id,
                    full_name=person.name,
                    films=[],
                ),
            )

    return person_resp


# Внедряем PersonService с помощью Depends(get_person_service)
@router.get("/{person_id}/film", response_model=list[Film])
async def person_films(
    person_id: str = Path(
        description="Persons's UUID",
        example="8b197ae2-38c2-48c7-8cf6-6dc234d16efb",
        regex=fast_api_conf.UUID_REGEXP,
    ),
    person_service: PersonService = Depends(get_person_service),
) -> list[Film]:
    """Return a person's films (only films list).

    Raises:
        HTTPException: If requested person or films not found.
    """
    person = await person_service.get_by_id(person_id)
    if not person:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail="Person not found",
        )

    films = await person_service.get_person_films(person_id, person.name)
    if not films:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail="Films not found",
        )

    return [Film.parse_obj(x) for x in films]


@router.get("/{person_id}/", response_model=Person)
async def person(
    person_id: str = Path(
        description="Persons's UUID",
        example="8b197ae2-38c2-48c7-8cf6-6dc234d16efb",
        regex=fast_api_conf.UUID_REGEXP,
    ),
    person_service: PersonService = Depends(get_person_service),
) -> Person:
    """Return a person's films (only uuid) and roles (as a list).

    Raises:
        HTTPException: If requested person not found.
    """
    person_model = await person_service.get_by_id(person_id)
    if not person_model:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail="Person not found",
        )

    films = await person_service.get_person_films(person_id, person_model.name)
    if films:
        return Person(
            uuid=person_model.id,
            full_name=person_model.name,
            films=Person.get_films_roles(
                person_name=person_model.name,
                films=films,
            ),
        )
    return Person(
        uuid=person_model.id,
        full_name=person_model.name,
        films=[],
    )
