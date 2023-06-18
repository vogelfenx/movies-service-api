from fastapi import FastAPI
from fastapi.responses import ORJSONResponse


from api.v1.films import routes as films_v1
from api.v1.genres import routes as genres_v1
from api.v1.persons import routes as persons_v1
from core.config import es_conf, fast_api_conf, redis_conf
from db.cache import dependency as cache_dependency
from db.cache.redis import RedisCache
from db.search import dependency as search_dependency
from db.search.elastic.search import Search

app = FastAPI(
    title=fast_api_conf.PROJECT_NAME,
    docs_url="/api/openapi",
    openapi_url="/api/openapi.json",
    default_response_class=ORJSONResponse,
)


@app.on_event("startup")
async def startup():
    """Start dependency."""
    cache_dependency.cache = RedisCache(
        host=redis_conf.REDIS_HOST,
        port=redis_conf.REDIS_PORT,
    )
    search_dependency.db = Search(
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
    if cache_dependency.cache:
        await cache_dependency.cache.close()

    if search_dependency.db:
        await search_dependency.db.close()


# Теги указываем для удобства навигации по документации
app.include_router(
    films_v1.router,
    prefix="/api/v1/films",
    tags=["films"],
)
app.include_router(
    genres_v1.router,
    prefix="/api/v1/genres",
    tags=["genres"],
)
app.include_router(
    persons_v1.router,
    prefix="/api/v1/persons",
    tags=["persons"],
)
