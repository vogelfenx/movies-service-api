from http import HTTPStatus
from math import ceil
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Path, Query
from pydantic import BaseModel, Field

from api.messages import FILM_NOT_FOUND
from core.config import fast_api_conf
from models import Film
from models.common import ConfigOrjsonMixin
from services.film import FilmService, get_film_service

router = APIRouter()


class ResponseFilms(BaseModel):
    """Response model for the film list endpoints"""

    class _ResponseFilm(BaseModel):
        """Response film submodel"""

        id: UUID = Field(alias="uuid")
        title: str
        imdb_rating: float | None

        class Config(ConfigOrjsonMixin):
            allow_population_by_field_name = True

    films_count: int
    page_size: int
    total_pages: int | None = None
    page_number: int
    next_page: int | None = None
    prev_page: int | None = None
    films: list[_ResponseFilm] = Field(default_factory=list)

    def __init__(self, **data):
        super().__init__(**data)
        self.total_pages = ceil(self.films_count / self.page_size)

        self.next_page = self.page_number + 1 if self.page_number < self.total_pages else None
        self.prev_page = self.page_number - 1 if self.page_number > 1 else None

    class Config(ConfigOrjsonMixin):
        allow_population_by_field_name = True


async def pagination_parameters(
    page_size: Annotated[int, Query(
        description="The size of the results to retrieve per page",
        ge=1,
    )] = fast_api_conf.DEFAULT_ELASTIC_QUERY_SIZE,
    page_number: Annotated[int, Query(
        description="The page number to retrieve",
        ge=1,
    )] = 1
):
    """Common pagination parameters."""
    return {
        "page_size": page_size,
        "page_number": page_number
    }


PaginationParameters = Annotated[dict, Depends(pagination_parameters)]


@router.get("/search", response_model=ResponseFilms)
async def films_search(
    pagination_parameters: PaginationParameters,
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
    page_number = pagination_parameters["page_number"]
    page_size = pagination_parameters["page_size"]

    search_fields = ['title', 'description', 'director',
                     'actors_names', 'writers_names', 'genre']

    films_count, films = await film_service.get_films_list(
        page_size=page_size,
        page_number=page_number,
        search_query=query,
        search_fields=search_fields
    )

    return ResponseFilms(
        page_size=page_size,
        page_number=page_number,
        films_count=films_count,
        films=films
    )


@router.get("/", response_model=ResponseFilms, response_model_exclude_unset=True)
async def films_list(
    pagination_parameters: PaginationParameters,
    sort: Annotated[str | None, Query(
        description="Sort by rating e.g. `+imdb_rating` or `-imdb_rating`"
    )] = None,
    genre: Annotated[list[str] | None, Query(
        description="Filter by genre, e.g. `Action`"
    )] = None,
    film_service: FilmService = Depends(get_film_service),
) -> ResponseFilms:
    """
    ### Retrieve a paginated list of films.

    The list of retrieved films can optionally be filtered by genre and sorted by a specified order field.

    ### Query arguments:
    - **page_size**: The size of the films retrieved per page.
    - **page_number**: The page number to retrieve.
    - **sort**: The sort field and the sort direction.
    - **genre**: The genre(s) of films to retrieve.

    ### Returns:
    A dictionary containing the paginated list of `Film` objects,
    along with the total number of films and pagination details.
    """
    page_number = pagination_parameters["page_number"]
    page_size = pagination_parameters["page_size"]

    if genre:
        genre = {"genre": genre}

    if sort:
        order = "asc" if sort[0] == "+" else "desc" if sort[0] == "-" else None
        sort = {
            sort[1:]: {"order": order},
        }

    films_count, films = await film_service.get_films_list(
        page_size=page_size,
        page_number=page_number,
        sort_field=sort,
        filter_field=genre,
    )

    films = (
        Film(
            id=film.id,
            title=film.title,
            imdb_rating=film.imdb_rating,
        )
        for film in films
    )

    return ResponseFilms(
        page_size=page_size,
        page_number=page_number,
        films_count=films_count,
        films=films
    )


@router.get("/{film_id}/", response_model=Film, response_model_exclude_unset=True)
async def film_details(
    film_id: Annotated[UUID, Path(description="ID of the film to retrieve")],
    film_service: FilmService = Depends(get_film_service)
) -> Film:
    """
    ### Retrieve the details of a specific film.

    ### Path arguments:
    - **film_id**: The ID of the film to retrieve

    ### Returns:
    The film with the details.
    """
    film = await film_service.get_by_id(film_id)

    if not film:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail=FILM_NOT_FOUND)

    return Film(
        id=film.id,
        title=film.title,
        imdb_rating=film.imdb_rating,
        description=film.description,
        genre=film.genre,
        actors=film.actors,
        writers=film.writers,
        director=film.director,
    )
