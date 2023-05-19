from http import HTTPStatus

from core.config import fast_api_conf
from core.messages import GENRE_NOT_FOUND
from fastapi import APIRouter, Depends, HTTPException, Path

from .models import GenreResponse
from .service import GenreService, get_genres_service

router = APIRouter()


@router.get("/", response_model=list[GenreResponse])
async def genres(
    genre_service: GenreService = Depends(get_genres_service),
) -> list[GenreResponse]:
    """Return genres.

    Raises:
        HTTPException: If requested genres not found.
    """
    genres_list = await genre_service.get_all()
    if not genres_list:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail=GENRE_NOT_FOUND,
        )

    return [GenreResponse(uuid=x.id, name=x.name) for x in genres_list]


@router.get("/{genre_id}", response_model=GenreResponse)
async def genre(
    genre_id: str = Path(
        description="Genre's UUID",
        example="3d8d9bf5-0d90-4353-88ba-4ccc5d2c07ff",
        regex=fast_api_conf.UUID_REGEXP,
    ),
    genre_service: GenreService = Depends(get_genres_service),
) -> GenreResponse:
    """Return a genre by id.

    Raises:
        HTTPException: If requested genre not found.
    """
    genre_model = await genre_service.get_by_id(genre_id)
    if not genre_model:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail=GENRE_NOT_FOUND,
        )

    return GenreResponse.parse_obj(genre_model)
