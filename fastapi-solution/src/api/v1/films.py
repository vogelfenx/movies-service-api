from http import HTTPStatus
from typing import Annotated, Dict, List, Optional, Union

from fastapi import APIRouter, Depends, HTTPException, Query

from core.config import fast_api_conf
from models import Film
from services.film import FilmService, get_film_service

router = APIRouter()


@router.get("/", response_model=dict, response_model_exclude_unset=True)
async def films_list(
    page_size: Optional[int] = fast_api_conf.DEFAULT_ELASTIC_QUERY_SIZE,
    page_number: Optional[int] = 1,
    sort: Optional[str] = None,
    genre: Annotated[list[str] | None, Query()] = None,
    search: Optional[str] = None,
    film_service: FilmService = Depends(get_film_service),
) -> Dict[str, Union[int, List[Film], None]]:
    """
    Retrieve a paginated list of films.

    The list of retrieved films can optionally be filtered by genre and sorted by a specified order field.

    Args:
        page_size (Optional[int]): The size of the films retrieved per page.
            Defaults to `DEFAULT_ELASTIC_QUERY_SIZE`.
        page_number (Optional[int]): The page number to retrieve. Default is 1.
        sort (Optional[str]): The sort field and the sort direction.
        genre (Annotated[list[str] | None, Query()]): The genre(s) of films to retrieve.
        search: Optional[str]: The phrase to search.
        film_service (FilmService): Film service to retrieve films from the database.

    Returns:
         A dictionary containing the paginated list of `Film` objects,
         along with the total number of films and pagination details.
         For example:

        {
            'films_count': 10,
            'total_pages': 5,
            'next_page': 3,
            'prev_page': 1,
            'films': [{
                    'id': "50fb4de9-e4b3-4aca-9f2f-00a48f12f9b3",
                    'title': "Star Trek: First Contact",
                    'imdb_rating':7.6}]
        }

    Raises:
        HTTPException: If requested page not found or list of films is empty
         or given sort parameter not found.
    """
    if not page_number > 0:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="page not found")

    if genre:
        genre = {"genre": genre}

    if sort:
        order = "asc" if sort[0] == "+" else "desc" if sort[0] == "-" else None
        sort = {
            sort[1:]: {"order": order},
        }

    try:
        films_count, films = await film_service.get_films_list(
            page_size=page_size,
            page_number=page_number,
            sort_field=sort,
            filter_field=genre,
            search_query=search,
        )
    except HTTPException as error:
        raise HTTPException(status_code=error.status_code, detail=error.detail)

    films = (
        Film(
            id=film.id,
            title=film.title,
            imdb_rating=film.imdb_rating,
        )
        for film in films
    )
    if not films:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="films not found")

    total_pages = films_count // page_size
    total_pages += 1 if films_count % page_size > 0 else 0

    next_page = page_number + 1 if page_number < total_pages else None
    prev_page = page_number - 1 if page_number > 1 else None

    return {
        "films_count": films_count,
        "total_pages": total_pages,
        "next_page": next_page,
        "prev_page": prev_page,
        "films": films,
    }


@router.get("/{film_id}", response_model=Film, response_model_exclude_unset=True)
async def film_details(
    film_id: str, film_service: FilmService = Depends(get_film_service)
) -> Film:
    """
    Retrieve the details of a specific film.

    Args:
        film_id (str): The ID of the film to retrieve.
        film_service (FilmService): Film service to retrieve films from the database.

    Raises:
        HTTPException: If the film with the specified ID cannot be found.

    Returns:
        Film: The film with the details.
    """
    film = await film_service.get_by_id(film_id)
    if not film:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="film not found")

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
