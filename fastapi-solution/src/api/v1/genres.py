from http import HTTPStatus
from typing import List

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from uuid import UUID

from services.genre import GenreService, get_genres_service

router = APIRouter()


class Genre(BaseModel):
    id: UUID = Field(alias="uuid")
    name: str

    class Config:
        allow_population_by_field_name = True


# Внедряем GenreService с помощью Depends(get_genre_service)
@router.get("/", response_model=List[Genre])
async def genres(
    genre_service: GenreService = Depends(get_genres_service),
) -> List[Genre]:
    genres = await genre_service.get_all()
    if not genres:
        # Если жанры не найдены, отдаём 404 статус
        # Желательно пользоваться уже определёнными HTTP-статусами, которые содержат enum
        # Такой код будет более поддерживаемым
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="genres not found")

    # Перекладываем данные из models.Genre в Genre
    # Обратите внимание, что у модели бизнес-логики есть поле description
    # Которое отсутствует в модели ответа API.
    # Если бы использовалась общая модель для бизнес-логики и формирования ответов API
    # вы бы предоставляли клиентам данные, которые им не нужны
    # и, возможно, данные, которые опасно возвращать
    genres_resp = [Genre(uuid=x.id, name=x.name) for x in genres]
    return genres_resp


# Внедряем GenreService с помощью Depends(get_genre_service)
@router.get("/{genre_id}", response_model=Genre)
async def genre(
    genre_id: str,
    genre_service: GenreService = Depends(get_genres_service),
) -> Genre:
    genre = await genre_service.get_by_id(genre_id)
    if not genre:
        # Если жанры не найдены, отдаём 404 статус
        # Желательно пользоваться уже определёнными HTTP-статусами, которые содержат enum
        # Такой код будет более поддерживаемым
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail="genre id=<{0}> not found".format(genre_id),
        )

    # Перекладываем данные из models.Genre в Genre
    # Обратите внимание, что у модели бизнес-логики есть поле description
    # Которое отсутствует в модели ответа API.
    # Если бы использовалась общая модель для бизнес-логики и формирования ответов API
    # вы бы предоставляли клиентам данные, которые им не нужны
    # и, возможно, данные, которые опасно возвращать

    return Genre.parse_obj(genre)
