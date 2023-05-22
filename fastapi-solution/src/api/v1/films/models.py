"""Response model and etc for api."""
from pydantic import BaseModel, Field
from uuid import UUID
from models.common import ConfigOrjsonMixin
from math import ceil
from fastapi import Query
from core.config import es_conf
from typing import Annotated


class ResponseFilms(BaseModel):
    """Response model for the film list endpoints."""

    class _ResponseFilm(BaseModel):
        """Response film submodel."""

        id: UUID = Field(alias="uuid")
        title: str
        imdb_rating: float | None

        class Config(ConfigOrjsonMixin):
            """Config for aliasing."""

            allow_population_by_field_name = True

    films_count: int
    page_size: int
    total_pages: int | None = None
    page_number: int
    next_page: int | None = None
    prev_page: int | None = None
    films: list[_ResponseFilm] = Field(default_factory=list)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.total_pages = ceil(self.films_count / self.page_size)

        self.next_page = (
            self.page_number + 1
            if self.page_number < self.total_pages
            else None
        )
        self.prev_page = self.page_number - 1 if self.page_number > 1 else None

    class Config(ConfigOrjsonMixin):
        """Config for aliasing."""

        allow_population_by_field_name = True


async def pagination_parameters(
    page_size: Annotated[
        int,
        Query(
            description="The size of the results to retrieve per page",
            ge=1,
        ),
    ] = es_conf.DEFAULT_ELASTIC_QUERY_SIZE,
    page_number: Annotated[
        int,
        Query(
            description="The page number to retrieve",
            ge=1,
        ),
    ] = 1,
):
    """Define common pagination parameters."""
    return {
        "page_size": page_size,
        "page_number": page_number,
    }
