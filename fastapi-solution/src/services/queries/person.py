def person_films_query(person_id: str, name: str):
    """Create a query for ES which would search by id and name.

    Args:
        person_id (str): A person UUID.
        name (str): Must be full_name of person.
    """
    return {
        "query": {
            "bool": {
                "should": [
                    {
                        "nested": {
                            "path": "actors",
                            "query": {
                                "term": {"actors.id": person_id},
                            },
                        },
                    },
                    {
                        "nested": {
                            "path": "writers",
                            "query": {
                                "term": {"writers.id": person_id},
                            },
                        },
                    },
                    {
                        "match_phrase": {"director": name},
                    },
                ],
            },
        },
    }


def person_search_query(name: str):
    """Create a query for ES which would search by name.

    Args:
        name (str): May be first name or last name of person.
    """
    return {
        "match": {"name": name},
    }
