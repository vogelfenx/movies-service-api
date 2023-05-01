from elasticsearch import AsyncElasticsearch

es: AsyncElasticsearch | None = None


# Функция понадобится при внедрении зависимостей
async def get_elastic() -> AsyncElasticsearch | None:
    return es
