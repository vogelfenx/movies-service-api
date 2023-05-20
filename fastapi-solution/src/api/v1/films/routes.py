from http import HTTPStatus
from typing import Annotated
from uuid import UUID

from core.messages import FILM_NOT_FOUND
from fastapi import APIRouter, Depends, HTTPException, Path, Query
from models import Film
from .service import FilmService, get_film_service
from .models import ResponseFilms, pagination_parameters

router = APIRouter()

PaginationParameters = Annotated[dict, Depends(pagination_parameters)]


@router.get("/search", response_model=ResponseFilms)
async def films_search(
    pagination_params: PaginationParameters,
    query: Annotated[str, Query(description="Search by query")],
    film_service: FilmService = Depends(get_film_service),
) -> ResponseFilms:
    """
    ### Retrieve a paginated list of films that match the search query.

    Search across predefined fields.

    ### Query arguments:
    - **page_size**: The size of the films retrieved per page.
    - **page_number**: The page number to retrieve.
    - **query**: The phrase to search.

    ### Returns:
    A dictionary containing the paginated list of `Film` objects,
    along with the total number of films and pagination details.
    """
    page_number = pagination_params["page_number"]
    page_size = pagination_params["page_size"]

    search_fields = [
        "title",
        "description",
        "director",
        "actors_names",
        "writers_names",
        "genre",
    ]

    films_count, films = await film_service.get_films_list(
        page_size=page_size,
        page_number=page_number,
        search_query=query,
        search_fields=search_fields,
    )

    return ResponseFilms(
        page_size=page_size,
        page_number=page_number,
        films_count=films_count,
        films=films,
    )


@router.get(
    "/",
    response_model=ResponseFilms,
    response_model_exclude_unset=True,
)
async def films_list(
    pagination_params: PaginationParameters,
    sort: Annotated[
        str | None,
        Query(
            description="Sort by rating e.g. `+imdb_rating` or `-imdb_rating`",
        ),
    ] = None,
    genre: Annotated[
        list[str] | None,
        Query(
            description="Filter by genre, e.g. `Action`",
        ),
    ] = None,
    film_service: FilmService = Depends(get_film_service),
) -> ResponseFilms:
    """
    ### Retrieve a paginated list of films.

    The list of retrieved films can optionally be filtered by genre
    and sorted by a specified order field.

    ### Query arguments:
    - **page_size**: The size of the films retrieved per page.
    - **page_number**: The page number to retrieve.
    - **sort**: The sort field and the sort direction.
    - **genre**: The genre(s) of films to retrieve.

    ### Returns:
    A dictionary containing the paginated list of `Film` objects,
    along with the total number of films and pagination details.
    """
    page_number = pagination_params["page_number"]
    page_size = pagination_params["page_size"]

    genres = None
    sort_field = None

    if genre:
        genres = {"genre": genre}
    if sort:
        order = None
        if sort[0] == "+":
            order = "asc"
        elif sort[0] == "-":
            order = "desc"

        sort_field = {
            sort[1:]: {"order": order},
        }

    films_count, _films = await film_service.get_films_list(
        page_size=page_size,
        page_number=page_number,
        sort_field=sort_field,
        filter_field=genres,
    )

    films = (
        Film(
            uuid=film.id,
            title=film.title,
            imdb_rating=film.imdb_rating,
            description=None,
        )
        for film in _films
    )

    return ResponseFilms(
        page_size=page_size,
        page_number=page_number,
        films_count=films_count,
        films=films,
    )


@router.get(
    "/{film_id}/",
    response_model=Film,
    response_model_exclude_unset=True,
)
async def film_details(
    film_id: Annotated[UUID, Path(description="ID of the film to retrieve")],
    film_service: FilmService = Depends(get_film_service),
) -> Film:
    """
    ### Retrieve the details of a specific film.

    ### Path arguments:
    - **film_id**: The ID of the film to retrieve

    ### Returns:
    The film with the details.

    ### Raises:
        HTTPException: If film not found.
    """
    film = await film_service.get_by_id(film_id)

    if not film:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail=FILM_NOT_FOUND,
        )

    return Film(
        uuid=film.id,
        title=film.title,
        imdb_rating=film.imdb_rating,
        description=film.description,
        genre=film.genre,
        actors=film.actors,
        writers=film.writers,
        director=film.director,
    )
