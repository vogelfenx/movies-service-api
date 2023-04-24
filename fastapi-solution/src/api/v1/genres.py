from http import HTTPStatus
from typing import List

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from services.genre import GenreService, get_genres_service

router = APIRouter()


class Genre(BaseModel):
    uuid: str
    name: str


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
