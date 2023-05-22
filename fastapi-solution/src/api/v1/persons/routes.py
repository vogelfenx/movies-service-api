from http import HTTPStatus
from typing import Annotated

from core.config import es_conf, fast_api_conf
from core.messages import FILM_NOT_FOUND, PERSON_NOT_FOUND
from fastapi import APIRouter, Depends, HTTPException, Path, Query

from .models import FilmResponse, PersonResponse
from .service import PersonService, get_person_service

router = APIRouter()


@router.get("/search", response_model=list[PersonResponse])
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
    ] = es_conf.DEFAULT_ELASTIC_QUERY_SIZE,
    page_number: Annotated[
        int,
        Query(description="Number of page", ge=0),
    ] = 0,
    person_service: PersonService = Depends(get_person_service),
) -> list[PersonResponse]:
    """Search a person's films by query (part of name).

    Raises:
        HTTPException: If requested person not found.
    """
    person_resp: list[PersonResponse] = []
    persons = await person_service.get_persons_by_name(
        name=query,
        page_size=page_size,
        page_number=page_number,
    )
    if not persons:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail=PERSON_NOT_FOUND,
        )

    for person in persons:
        films = await person_service.get_person_films(
            person_id=str(person.id),
            person_name=person.name,
        )
        if films:
            person_resp.append(
                PersonResponse(
                    uuid=person.id,
                    full_name=person.name,
                    films=PersonResponse.get_films_roles(
                        person_name=person.name,
                        films=films,
                    ),
                ),
            )
        else:
            person_resp.append(
                PersonResponse(
                    uuid=person.id,
                    full_name=person.name,
                    films=[],
                ),
            )

    return person_resp


# Внедряем PersonService с помощью Depends(get_person_service)
@router.get("/{person_id}/film", response_model=list[FilmResponse])
async def person_films(
    person_id: str = Path(
        description="Persons's UUID",
        example="8b197ae2-38c2-48c7-8cf6-6dc234d16efb",
        regex=fast_api_conf.UUID_REGEXP,
    ),
    person_service: PersonService = Depends(get_person_service),
) -> list[FilmResponse]:
    """Return a person's films (only films list).

    Raises:
        HTTPException: If requested person or films not found.
    """
    person = await person_service.get_by_id(person_id)
    if not person:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail=PERSON_NOT_FOUND,
        )

    films = await person_service.get_person_films(person_id, person.name)
    if not films:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail=FILM_NOT_FOUND,
        )

    return [FilmResponse.parse_obj(x) for x in films]


@router.get("/{person_id}/", response_model=PersonResponse)
async def person(
    person_id: str = Path(
        description="Persons's UUID",
        example="8b197ae2-38c2-48c7-8cf6-6dc234d16efb",
        regex=fast_api_conf.UUID_REGEXP,
    ),
    person_service: PersonService = Depends(get_person_service),
) -> PersonResponse:
    """Return a person's films (only uuid) and roles (as a list).

    Raises:
        HTTPException: If requested person not found.
    """
    person_model = await person_service.get_by_id(person_id)
    if not person_model:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail=PERSON_NOT_FOUND,
        )

    films = await person_service.get_person_films(person_id, person_model.name)
    if films:
        return PersonResponse(
            uuid=person_model.id,
            full_name=person_model.name,
            films=PersonResponse.get_films_roles(
                person_name=person_model.name,
                films=films,
            ),
        )
    return PersonResponse(
        uuid=person_model.id,
        full_name=person_model.name,
        films=[],
    )
