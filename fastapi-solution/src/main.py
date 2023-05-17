from api.v1 import films, genres, persons
from core.config import fast_api_conf, es_conf, redis_conf
from core.search import Search
from db import search, redis
from elasticsearch import AsyncElasticsearch
from fastapi import FastAPI
from fastapi.responses import ORJSONResponse
from redis.asyncio import Redis

app = FastAPI(
    title=fast_api_conf.PROJECT_NAME,
    docs_url="/api/openapi",
    openapi_url="/api/openapi.json",
    default_response_class=ORJSONResponse,
)


@app.on_event("startup")
async def startup():
    """Start dependency."""
    redis.redis = Redis(host=redis_conf.REDIS_HOST, port=redis_conf.REDIS_PORT)
    search.db = Search(
        hosts=[
            "http://{host}:{port}".format(
                host=es_conf.ELASTIC_HOST,
                port=es_conf.ELASTIC_PORT,
            ),
        ],
    )


@app.on_event("shutdown")
async def shutdown():
    """Stop dependency."""
    if redis.redis:
        await redis.redis.close()

    if search.db:
        await search.db.close()


# Теги указываем для удобства навигации по документации
app.include_router(films.router, prefix="/api/v1/films", tags=["films"])
app.include_router(genres.router, prefix="/api/v1/genres", tags=["genres"])
app.include_router(persons.router, prefix="/api/v1/persons", tags=["persons"])
