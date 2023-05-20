from db.search.abc.query import SelectQuery


class QueryPersonByIdAndName(SelectQuery):
    """Create a query by id and name of person."""

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
        """Create a query for ES which would search by id and name."""
        return {
            "query": {
                "bool": {
                    "should": [
                        {
                            "nested": {
                                "path": "actors",
                                "query": {
                                    "term": {"actors.id": self.id},
                                },
                            },
                        },
                        {
                            "nested": {
                                "path": "writers",
                                "query": {
                                    "term": {"writers.id": self.id},
                                },
                            },
                        },
                        {
                            "match_phrase": {"director": self.name},
                        },
                    ],
                },
            },
        }


class QueryPersonByName(SelectQuery):
    """Create a query for ES which would search by name."""

    def __init__(
        self,
        name: str,
        fields: list[str] | None = None,
    ) -> None:
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
            "query": {
            "match": {"name": self.name},
            },
        }
