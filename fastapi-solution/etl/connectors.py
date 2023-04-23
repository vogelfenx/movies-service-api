import json

import psycopg2 as pg
from elasticsearch import Elasticsearch, helpers
from psycopg2.extras import DictCursor
from psycopg2.extras import register_uuid

from dataclasses import dataclass
from data_classes import Filmwork, GenreIds, PersonIds, FilmIds, PgDttmStr
from config import elastic_conf, pg_conf, dsl
from backoff_decorator import backoff


class ESconnector:

    def __init__(self) -> None:
        self.connection = None

    @backoff(start_sleep_time=elastic_conf.backoff_start_sleep_time,
             factor=elastic_conf.backoff_factor,
             border_sleep_time=elastic_conf.backoff_border_sleep_time,
             resourse_name='Elasticsearch')
    def __enter__(self):
        self.connection = Elasticsearch(host=elastic_conf.elastic_url)
        self.connection.cluster.health(wait_for_status='yellow',
                                       request_timeout=1)
        return self

    @backoff(start_sleep_time=elastic_conf.backoff_start_sleep_time,
             factor=elastic_conf.backoff_factor,
             border_sleep_time=elastic_conf.backoff_border_sleep_time,
             resourse_name='Elasticsearch')
    def has_index(self) -> bool:
        """
        Return is index exists

        :param index: index name
        """
        return self.connection.indices.exists(index=elastic_conf.index_name)

    @backoff(start_sleep_time=elastic_conf.backoff_start_sleep_time,
             factor=elastic_conf.backoff_factor,
             border_sleep_time=elastic_conf.backoff_border_sleep_time,
             resourse_name='Elasticsearch')
    def create_index(self) -> None:
        """
        Create elasticsearch index

        :param index: index name
        :param body: index structure
        """
        with open(elastic_conf.index_file_path, 'r') as f:
            self.connection.indices.create(index=elastic_conf.index_name,
                                           body=json.load(f))

    def load(self, block) -> None:
        """
        Load batch of docs in elasticsearch index.

        :param block: iterable block of data
        """
        if not block:
            return
        helpers.bulk(self.connection, block)
        #self.connection.bulk(body=body, index='movies')

    def __exit__(self, *args):
        self.connection.close()


class PGconnector:

    def __init__(self) -> None:
        self.connection = None

    @backoff(start_sleep_time=pg_conf.backoff_start_sleep_time,
             factor=pg_conf.backoff_factor,
             border_sleep_time=pg_conf.backoff_border_sleep_time,
             resourse_name='Postgres')
    def __enter__(self) -> None:
        self.connection = pg.connect(**dsl, cursor_factory=DictCursor)
        register_uuid()
        return self

    @backoff(start_sleep_time=pg_conf.backoff_start_sleep_time,
             factor=pg_conf.backoff_factor,
             border_sleep_time=pg_conf.backoff_border_sleep_time,
             resourse_name='Postgres')
    def get_pg_data(self, sql: str,
                    dataclass: dataclass,
                    params=None,
                    batch_size=None):
        """ 
        Fetch data from postgres by sql query
        :param sql: SQL query text
        :param params: params for SQL query
        :param size: size of query response batch
        """
        if params is None:
            params = []
        if self.connection.closed:
            self.connection = pg.connect(**dsl, cursor_factory=DictCursor)
        with self.connection.cursor() as cur:
            register_uuid()
            cur.execute(sql, vars=params)
            while batch_rows := cur.fetchmany(size=batch_size):
                yield [dataclass(*row) for row in batch_rows]

    def get_current_dttm(self) -> str:
        """
        Return current timestap in Postgres
        """
        res = next(self.get_pg_data(pg_conf.sql_get_cur_dttm,
                                    dataclass=PgDttmStr,
                                    batch_size=1))
        return res[0].dttm_str

    def get_upd_films(self, extr_type, etl_param):
        """
        Fetch updated films
        :param extr_type: Extraction algorithm
        Extract new films by
         fw - by filmwork table
         g - by genre table
         p - by person table
        :param etl_params: params for sql query
        """

        if extr_type == 'fw':
            return self.get_pg_data(sql=pg_conf.sql_fw_get_films,
                                    dataclass=Filmwork,
                                    params=etl_param,
                                    batch_size=pg_conf.bulk_size)
        elif extr_type == 'g':
            genre_ids = []
            genre_ids_list = [rows for rows in self.get_pg_data(sql=pg_conf.sql_g_get_genre_ids,
                                                                dataclass=GenreIds,
                                                                params=etl_param,
                                                                batch_size=pg_conf.bulk_size)]
            for rows in genre_ids_list:
                genre_ids += rows
            genre_ids_sql = tuple([g_id.genre_id for g_id in genre_ids])

            if not genre_ids_sql:
                return []

            fw_ids = []
            fw_ids_list = [rows for rows in self.get_pg_data(sql=pg_conf.sql_g_get_film_ids,
                                                             dataclass=FilmIds,
                                                             params=(genre_ids_sql,),
                                                             batch_size=pg_conf.bulk_size)]
            for rows in fw_ids_list:
                fw_ids += rows
            fw_ids_sql = tuple([fw_id.fw_id for fw_id in fw_ids])

            return self.get_pg_data(sql=pg_conf.sql_g_get_films,
                                    dataclass=Filmwork,
                                    params=(fw_ids_sql,),
                                    batch_size=pg_conf.bulk_size)
        elif extr_type == 'p':
            person_ids = []
            person_ids_list = [rows for rows in self.get_pg_data(sql=pg_conf.sql_p_get_person_ids,
                                                                 dataclass=PersonIds,
                                                                 params=etl_param,
                                                                 batch_size=pg_conf.bulk_size)]
            for rows in person_ids_list:
                person_ids += rows
            person_ids_sql = tuple([p_id.person_id for p_id in person_ids])

            if not person_ids_sql:
                return []

            fw_ids = []
            fw_ids_list = [rows for rows in self.get_pg_data(sql=pg_conf.sql_p_get_film_ids,
                                                             dataclass=FilmIds,
                                                             params=(person_ids_sql,),
                                                             batch_size=pg_conf.bulk_size)]
            for rows in fw_ids_list:
                fw_ids += rows
            fw_ids_sql = tuple([fw_id.fw_id for fw_id in fw_ids])

            return self.get_pg_data(sql=pg_conf.sql_p_get_films,
                                    dataclass=Filmwork,
                                    params=(fw_ids_sql,),
                                    batch_size=pg_conf.bulk_size)

    def __exit__(self, *args):
        self.connection.close()
