from json import load

from pydantic import BaseSettings, Field
import os

base_dir = os.path.dirname(os.path.abspath(__file__))


class BaseTestSettings(BaseSettings):
    es_host: str
    es_port: str

    redis_host: str
    redis_port: str

    service_url_port: int = Field(8000)
    service_url: str = Field("http://127.0.0.1")
    api_root_endpoint: str = Field("api/v1")

    class Config:
        env_file = f"{base_dir}/.env"


class MovieSettings(BaseTestSettings):
    es_index: str = "movies"
    es_id_field: str = "id"
    es_index_movies_mapping: dict = load(
        open(
            f"{base_dir}/testdata/es_movies_schema.json",
            "r",
        )
    )


class PersonSettings(BaseTestSettings):
    es_index: str = 'persons'
    es_id_field: str = 'id'
    es_index_movies_mapping: dict = load(
        open(f"{base_dir}/testdata/es_person_schema.json", 'r')
    )


base_settings = BaseTestSettings()  # type: ignore
movies_settings = MovieSettings()  # type: ignore
persons_settings = PersonSettings()  # type: ignore
