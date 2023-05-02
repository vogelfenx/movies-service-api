import os

from logging import config as logging_config
from pydantic import BaseSettings

from core.logger import LOGGING

# Применяем настройки логирования
logging_config.dictConfig(LOGGING)


class ApiConfig(BaseSettings):
    # Название проекта. Используется в Swagger-документации
    PROJECT_NAME: str

    # Настройки Redis
    REDIS_HOST: str
    REDIS_PORT: int

    # Настройки Elasticsearch
    ELASTIC_HOST: str
    ELASTIC_PORT: int

    MAX_ELASTIC_QUERY_SIZE = 10000
    DEFAULT_ELASTIC_QUERY_SIZE = 10

    # Корень проекта
    file_path = os.path.abspath(__file__)
    dir_path = os.path.dirname(file_path)
    BASE_DIR = os.path.dirname(dir_path)

    # Шаблон для UUID
    UUID_REGEXP = r"[\w\d]{8}-[\w\d]{4}-[\w\d]{4}-[\w\d]{4}-[\w\d]{12}"

    class Config:
        env_file = "../.env"
        case_sensitive = False


fast_api_conf = ApiConfig()  # type: ignore
