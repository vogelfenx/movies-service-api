import os

from logging import config as logging_config
from pydantic import BaseSettings

from core.logger import LOGGING

# Применяем настройки логирования
logging_config.dictConfig(LOGGING)


class CommonSettings(BaseSettings):
    """
    Общий конфиг-класс
    """

    # Корень проекта
    file_path = os.path.abspath(__file__)
    dir_path = os.path.dirname(file_path)
    BASE_DIR = os.path.dirname(dir_path)

    class Config:
        env_file = "../.env"
        case_sensitive = False


class ApiSettings(CommonSettings):
    """
    Класс с настройками FastAPI
    """

    # Название проекта. Используется в Swagger-документации
    PROJECT_NAME: str

    # Шаблон для UUID
    UUID_REGEXP = r"[\w\d]{8}-[\w\d]{4}-[\w\d]{4}-[\w\d]{4}-[\w\d]{12}"


class ESSettings(CommonSettings):
    """
    Класс с настройками Elasticsearch.
    """

    ELASTIC_HOST: str
    ELASTIC_PORT: int

    MAX_ELASTIC_QUERY_SIZE = 10000
    DEFAULT_ELASTIC_QUERY_SIZE = 10


class RedisSettings(CommonSettings):
    """
    Класс с настройками Redis.
    """

    REDIS_HOST: str
    REDIS_PORT: int
    REDIS_EXPIRE: int = 60 * 5  # 5 min


fast_api_conf = ApiSettings()  # type: ignore
es_conf = ESSettings()  # type: ignore
redis_conf = RedisSettings()  # type: ignore
