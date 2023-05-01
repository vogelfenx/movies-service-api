from http import HTTPStatus
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Path
from pydantic import BaseModel, Field
from services.genre import GenreService, get_genres_service
from core import config

router = APIRouter()


class Genre(BaseModel):
    id: UUID = Field(alias="uuid")
    name: str

    class Config:
        allow_population_by_field_name = True


# Внедряем GenreService с помощью Depends(get_genre_service)
@router.get("/", response_model=list[Genre])
async def genres(
    genre_service: GenreService = Depends(get_genres_service),
) -> list[Genre]:
    """Returns genres"""

    genres = await genre_service.get_all()
    if not genres:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail="Genres not found"
        )

    genres_resp = [Genre(uuid=x.id, name=x.name) for x in genres]
    return genres_resp


# Внедряем GenreService с помощью Depends(get_genre_service)
@router.get("/{genre_id}", response_model=Genre)
async def genre(
    genre_id: str = Path(
        description="Genre's UUID",
        example="3d8d9bf5-0d90-4353-88ba-4ccc5d2c07ff",
        regex=config.UUID_REGEXP,
    ),
    genre_service: GenreService = Depends(get_genres_service),
) -> Genre:
    """Return a genre by id"""
    genre = await genre_service.get_by_id(genre_id)
    if not genre:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail="Genre id=<{0}> not found".format(genre_id),
        )

    return Genre.parse_obj(genre)
