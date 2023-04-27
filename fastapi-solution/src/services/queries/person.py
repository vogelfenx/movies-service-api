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
