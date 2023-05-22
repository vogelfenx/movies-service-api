from uuid import UUID
from pydantic import BaseModel, Field
from models.film import Film
from models.common import UUIDMixin


class FilmRolesResponse(UUIDMixin, BaseModel):
    """Response nested model contains film uuid and roles."""

    roles: list[str] = Field(default_factory=list)

    class Config:
        """Config for aliases."""

        allow_population_by_field_name = True


class PersonResponse(UUIDMixin, BaseModel):
    """Response person model with only specific fields."""

    name: str = Field(alias="full_name")
    films: list[FilmRolesResponse] = Field(default_factory=list)

    class Config:
        """Config for aliases."""

        allow_population_by_field_name = True

    @classmethod
    def get_films_roles(
        cls,
        person_name: str,
        films: list[Film],
    ) -> list[FilmRolesResponse]:
        """Extract roles from films."""
        films_roles = []
        for film in films:
            roles = []

            a = film.actors
            w = film.writers
            d = film.director
            if a:
                if list(
                    filter(
                        lambda x: True
                        if x and x.name == person_name
                        else False,
                        a,
                    ),
                ):
                    roles.append("actor")
            if w:
                if list(
                    filter(
                        lambda x: True
                        if x and x.name == person_name
                        else False,
                        w,
                    ),
                ):
                    roles.append("writer")
            if d and person_name in d:
                roles.append("director")

            films_roles.append(FilmRolesResponse(uuid=film.id, roles=roles))

        return films_roles


class FilmResponse(BaseModel):
    """Response film model with only specific fields."""

    id: UUID = Field(alias="uuid")
    title: str
    imdb_rating: float

    class Config:
        """Config for aliases."""

        allow_population_by_field_name = True
