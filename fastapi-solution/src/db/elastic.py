from typing import Optional
from elasticsearch import AsyncElasticsearch

es: Optional[AsyncElasticsearch]


# Функция понадобится при внедрении зависимостей
async def get_elastic() -> Optional[AsyncElasticsearch]:
    return es
