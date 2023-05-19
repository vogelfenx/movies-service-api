from json import load

from pydantic import BaseSettings, Field


class BaseTestSettings(BaseSettings):
    es_host: str
    es_port: str

    redis_host: str
    redis_port: str

    service_url: str = Field("http://127.0.0.1:8000")

    class Config:
        env_file = "fastapi-solution/tests/.env"


class MovieSettings(BaseTestSettings):
    es_index: str = "movies"
    es_id_field: str = "id"
    es_index_movies_mapping: dict = load(
        open(
            "fastapi-solution/tests/functional/testdata/es_movies_schema.json",
            "r",
        )
    )


base_settings = BaseTestSettings()  # type: ignore
movies_settings = MovieSettings()  # type: ignore
