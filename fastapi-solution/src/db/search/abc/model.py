from pydantic import BaseModel, Field


class IndexMixin(BaseModel):
    """Every index has a name, so it is in Mixin."""

    index: str = Field(alias="_index")

    class Config:
        allow_population_by_field_name = True


class QueryModel(BaseModel):
    """Query model for a search."""

    query: dict
    fields: list[str] | None = Field(default_factory=list)

    class Config:
        arbitrary_types_allowed = True
