from http import HTTPStatus
from uuid import UUID

from core import config
from fastapi import APIRouter, Depends, HTTPException, Path
from pydantic import BaseModel, Field
from services.genre import GenreService, get_genres_service

router = APIRouter()


class Genre(BaseModel):
    """Genre response model."""

    id: UUID = Field(alias="uuid")
    name: str

    class Config:
        """Config for aliasing."""

        allow_population_by_field_name = True


@router.get("/", response_model=list[Genre])
async def genres(
    genre_service: GenreService = Depends(get_genres_service),
) -> list[Genre]:
    """Return genres.

    Raises:
        HTTPException: If requested genres not found.
    """
    genres_list = await genre_service.get_all()
    if not genres_list:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail="Genres not found",
        )

    return [Genre(uuid=x.id, name=x.name) for x in genres_list]


@router.get("/{genre_id}", response_model=Genre)
async def genre(
    genre_id: str = Path(
        description="Genre's UUID",
        example="3d8d9bf5-0d90-4353-88ba-4ccc5d2c07ff",
        regex=config.UUID_REGEXP,
    ),
    genre_service: GenreService = Depends(get_genres_service),
) -> Genre:
    """Return a genre by id.

    Raises:
        HTTPException: If requested genre not found.
    """
    genre_model = await genre_service.get_by_id(genre_id)
    if not genre_model:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail="Genre id=<{0}> not found".format(genre_id),
        )

    return Genre.parse_obj(genre_model)
