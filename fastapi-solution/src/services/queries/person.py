def person_films_query(id, name):
    query = {
        "query": {
            "bool": {
                "should": [
                    {
                        "nested": {
                            "path": "actors",
                            "query": {
                                "term": {"actors.id": id},
                            },
                        },
                    },
                    {
                        "nested": {
                            "path": "writers",
                            "query": {
                                "term": {"writers.id": id},
                            },
                        },
                    },
                    {
                        "match_phrase": {"director": name},
                    },
                ]
            }
        },
    }
    return query


def person_search_query(name: str):
    """
    Returns a query for ES which would search by name

    Args:
        name (str): May be first name or last name of person
    """
    query = {
        "match": {"name": name},
    }
    return query
