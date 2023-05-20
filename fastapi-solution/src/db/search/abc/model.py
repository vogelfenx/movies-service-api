from pydantic import BaseModel, Field


class IndexMixin(BaseModel):
    index: str = Field(alias="_index")

    class Config:
        allow_population_by_field_name = True


class QueryModel(BaseModel):
    query: dict
    fields: list[str] | None = Field(default_factory=list)

    class Config:
        arbitrary_types_allowed = True
