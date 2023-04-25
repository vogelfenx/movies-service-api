from http import HTTPStatus
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException

from core import config
from models import Film
from services.film import FilmService, get_film_service

router = APIRouter()


@router.get("/", response_model=dict, response_model_exclude_unset=True)
async def films_list(
    page_size: Optional[int] = config.DEFAULT_ELASTIC_QUERY_SIZE,
    page_number: Optional[int] = 1,
    film_service: FilmService = Depends(get_film_service),
) -> list[Film]:
    """
    Retrieve list of films.

    The query parameters page_size and page_number can be used to paginate the result.

    Args:
        page_size (Optional[int]): The size of the films retrieved per page. Defaults to DEFAULT_ELASTIC_QUERY_SIZE.
        page_number (Optional[int]): The page number to retrieve. Default is 1.
        film_service (FilmService): Film service to retrieve films from the database.

    Raises:
        HTTPException: If requested page not found (HTTPStatus.NOT_FOUND).
        HTTPException: If films cannot be found (HTTPStatus.NOT_FOUND).

    Returns:
        list[Film]: List of films.
    """
    if not page_number > 0:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND,
                            detail="page not found")

    films_count, films = await film_service.get_films_list(page_size, page_number)
    films = (
        Film(
            id=film.id,
            title=film.title,
            imdb_rating=film.imdb_rating,
        ) for film in films
    )
    if not films:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND,
                            detail="films not found")

    total_pages = films_count // page_size
    total_pages += 1 if films_count % page_size > 0 else 0

    next_page = page_number + 1 if page_number < total_pages else None
    prev_page = page_number - 1 if page_number > 1 else None

    return {
        'films_count': films_count,
        'total_pages': total_pages,
        'next_page': next_page,
        'prev_page': prev_page,
        'films': films,
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
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND,
                            detail="film not found")

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
