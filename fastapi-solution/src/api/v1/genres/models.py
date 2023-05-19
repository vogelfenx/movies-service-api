from uuid import UUID
from pydantic import BaseModel, Field


class GenreResponse(BaseModel):
    """Genre response model."""

    id: UUID = Field(alias="uuid")
    name: str

    class Config:
        """Config for aliasing."""

        allow_population_by_field_name = True
