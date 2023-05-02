from api.v1 import films, genres, persons
from core.config import fast_api_conf
from db import elastic, redis
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
    redis.redis = Redis(host=fast_api_conf.REDIS_HOST, port=fast_api_conf.REDIS_PORT)
    elastic.es = AsyncElasticsearch(
        hosts=[
            "http://{host}:{port}".format(
                host=fast_api_conf.ELASTIC_HOST,
                port=fast_api_conf.ELASTIC_PORT,
            ),
        ],
    )


@app.on_event("shutdown")
async def shutdown():
    """Stop dependency."""
    if redis.redis:
        await redis.redis.close()
    if elastic.es:
        await elastic.es.close()


# Теги указываем для удобства навигации по документации
app.include_router(films.router, prefix="/api/v1/films", tags=["films"])
app.include_router(genres.router, prefix="/api/v1/genres", tags=["genres"])
app.include_router(persons.router, prefix="/api/v1/persons", tags=["persons"])
