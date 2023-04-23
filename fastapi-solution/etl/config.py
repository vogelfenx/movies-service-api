import configparser

from pydantic import BaseSettings

config = configparser.ConfigParser(interpolation=None)

config.read('etl_config/settings.ini')


class PostgresSettings(BaseSettings):

    postgres_db: str
    postgres_user: str
    postgres_password: str
    postgres_port: str
    postgres_schema: str
    postgres_host: str

    bulk_size: int

    sql_get_cur_dttm: str

    sql_fw_get_films: str

    sql_g_get_genre_ids: str
    sql_g_get_film_ids: str
    sql_g_get_films: str

    sql_p_get_person_ids: str
    sql_p_get_film_ids: str
    sql_p_get_films: str

    backoff_start_sleep_time: float
    backoff_factor: float
    backoff_border_sleep_time: float

    class Config:
        env_file = '../.env'
        case_sensitive = False


class EtlSettings(BaseSettings):
    sleep_time: float
    storage_file_path: str
    log_file_path: str

    state_template = {
                      'fw':
                      {'start_load': '1970-01-01 00:00:00',
                       'end_load': None,
                       'is_done': False
                       },
                      'g':
                      {'start_load': '1970-01-01 00:00:00',
                       'end_load': None,
                       'is_done': False
                       },
                      'p':
                      {'start_load': '1970-01-01 00:00:00',
                       'end_load': None,
                       'is_done': False
                       }
                      }


class ElasticSettings(BaseSettings):
    backoff_start_sleep_time: float
    backoff_factor: float
    backoff_border_sleep_time: float
    elastic_url: str
    index_name: str
    index_file_path: str


etl_conf = EtlSettings.parse_obj(config['etl'])
pg_conf = PostgresSettings.parse_obj(config['postgres'])
elastic_conf = ElasticSettings.parse_obj(config['elastic'])
dsl = {
        'dbname': pg_conf.postgres_db,
        'user': pg_conf.postgres_user,
        'password': pg_conf.postgres_password,
        'host': pg_conf.postgres_host,
        'port': pg_conf.postgres_port,
        'options': f"-c search_path={pg_conf.postgres_schema}"
    }
