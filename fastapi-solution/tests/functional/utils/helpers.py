from typing import Any
import json


def paginate_list(data_list: list[Any], page_size: int, page: int) -> list[Any]:
    offset = page_size * (page - 1)
    limit = page_size*page
    return data_list[offset:limit]


def get_es_bulk_query(es_test_data: list[dict], es_index: str, es_id_field: str):
    bulk_query = []

    for row in es_test_data:
        bulk_query.extend([
            json.dumps({'index': {'_index': es_index,
                       '_id': row[es_id_field]}}),
            json.dumps(row)
        ])
    query = '\n'.join(bulk_query) + '\n'

    return query
