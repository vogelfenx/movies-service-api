import sqlite3
import logging
import os
from dataclasses import dataclass
from contextlib import contextmanager, closing

import psycopg2
from psycopg2.extensions import connection as _connection
from psycopg2.extras import DictCursor
from psycopg2.extras import execute_batch
from psycopg2.extras import register_uuid

from table_classes import FilmWork, Genre, Person, \
    GenreFilmWork, PersonFilmWork


log = logging.getLogger(__name__)
logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

BATCH_SIZE = 100
TABLES_X_CLASSES = {
    'film_work': FilmWork,
    'genre': Genre,
    'person': Person,
    'genre_film_work': GenreFilmWork,
    'person_film_work': PersonFilmWork
}


@contextmanager
def sqlite_connection(db_path: str):
    try:
        connection = sqlite3.connect(db_path)
        yield connection
    finally:
        connection.close()


class SQLiteExtractor:
    def __init__(self,
                 sqlt_connection: sqlite3.Connection,
                 table: str,
                 data_class: dataclass):
        self.extraction_table = table
        self.sqlt_conn = sqlt_connection
        self.data_class = data_class

        self.cursor = self.sqlt_conn.cursor()
        self.cursor.row_factory = self.data_class.custom_row_factory

        self.extraction_query = f'SELECT * FROM {self.extraction_table};'
        log.info(f'Запрос выгрузки из SQLite-таблицы {self.extraction_table}')
        log.info(self.extraction_query)

    def extract_data(self):
        """Метод, реализующий захват данных из таблицы"""
        self.cursor.execute(self.extraction_query)
        while batch_rows := self.cursor.fetchmany(size=BATCH_SIZE):
            yield [row.get_values() for row in batch_rows]

        self.cursor.close()


class PostgresSaver:
    def __init__(self,
                 pg_connection: _connection,
                 table: str,
                 data_class: dataclass):
        self.target_table = table
        self.column_list = data_class.__dataclass_fields__.keys()
        self.insert_query = f"INSERT INTO {self.target_table}" \
                            f"({', '.join(self.column_list)}) " \
                            f"VALUES" \
                            f"({', '.join(['%s' for _ in self.column_list])})"
        self.cur = pg_connection.cursor()
        pg_connection.autocommit = True
        register_uuid()  # необходимо для успешного приведения типа uuid.UUID

    def load_data(self, data):
        """Метод, осуществляющий загрузку данных в Postgres"""
        log.info(f'Чистим Postgres-таблицу {self.target_table}')
        self.cur.execute(f'truncate table {self.target_table} cascade;')

        log.info(f'Загружаем данные в Postgres-таблицу {self.target_table}')
        log.info(self.insert_query)

        for batch in data:
            execute_batch(self.cur, self.insert_query,
                          batch, page_size=BATCH_SIZE)


def load_from_sqlite(connection: sqlite3.Connection,
                     pg_conn: _connection,
                     table: str, data_class: dataclass):
    """Основной метод загрузки данных из SQLite в Postgres"""
    log.info(f'###{table}###: cтарт!')
    try:
        sqlite_extractor = SQLiteExtractor(connection, table, data_class)
        sqlite_data = sqlite_extractor.extract_data()
    except Exception:
        log.exception(f'Ошибка при выгрузке данных из SQLite-таблицы {table}!')

    try:
        postgres_saver = PostgresSaver(pg_conn, table, data_class)
        postgres_saver.load_data(sqlite_data)
    except Exception:
        log.exception(f'Ошибка при вставке данных в Postgre-таблицу {table}!')


if __name__ == '__main__':
    dsl = {
        'dbname': os.getenv('POSTGRES_DB'),
        'user': os.getenv('POSTGRES_USER'),
        'password': os.getenv('POSTGRES_PASSWORD'),
        'host': os.getenv('POSTGRES_HOST'),
        'port': int(os.getenv('POSTGRES_PORT')),
        'options': f"-c search_path={os.getenv('POSTGRES_SCHEMA')}"
    }
    with sqlite_connection('db.sqlite') as sqlite_conn, \
        closing(psycopg2.connect(**dsl,
                                 cursor_factory=DictCursor)
                ) as pg_conn:
        for table, table_class in TABLES_X_CLASSES.items():
            log.info("Старт процесса выгрузки данных!")
            load_from_sqlite(sqlite_conn,
                             pg_conn, table=table,
                             data_class=table_class)
            log.info("\t")
