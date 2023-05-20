from db.search.abc.query import SelectQuery


class QueryFilm(SelectQuery):
    """Create a query by id and name of person.

    Args:
            query_size: The size of the query to retrieve.
            from_index: The document number to return from.
            sort_field: The field to sort the results by.
            filter_field: The field to filter the results by.
            search_query: The phrase to search.
            search_fields: The fields to search in.
    """

    def __init__(
        self,
        fields: list[str] | None = None,
        sort_field: dict[str, dict[str, str | None]] | None = None,
        filter_field: dict[str, list[str]] | None = None,
        search_query: str | None = None,
        search_fields: list[str] | None = None,
    ) -> None:
        self._fields = fields
        self.sort_field = sort_field
        self.filter_field = filter_field
        self.search_query = search_query
        self.search_fields = search_fields

        super().__init__()

    @property
    def fields(self) -> list[str] | None:
        return self._fields

    @property
    def query(self):
        """Create a query for ES which would search by id and name."""
        _query: dict = {
            "query": {
                "bool": {
                    "must": {
                        "match_all": {},
                    },
                },
            },
        }

        if self.filter_field:
            _query["query"]["bool"]["filter"] = {
                "terms": self.filter_field,
            }

        if self.sort_field:
            _query["sort"] = [self.sort_field]

        if self.search_query and self.search_fields:
            _query["query"]["bool"]["must"] = {
                "multi_match": {
                    "query": self.search_query,
                    "fields": self.search_fields,
                    "fuzziness": "AUTO",
                    "operator": "and",
                },
            }

        return _query


class QueryPersonName(SelectQuery):
    """Create a query for ES which would search by name."""

    def __init__(
        self,
        id: str,
        name: str,
        fields: list[str] | None = None,
    ) -> None:
        self.id = id
        self.name = name
        self._fields = fields
        super().__init__()

    @property
    def fields(self) -> list[str] | None:
        return self._fields

    @property
    def query(self):
        """The query for ES which would search by name."""
        return {
            "match": {"name": self.name},
        }
