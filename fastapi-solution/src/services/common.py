"""This file contains common functions or class for services."""
import orjson
from core.logger import get_logger

logger = get_logger(__name__)


def prepare_key_by_args(**kwargs) -> bytes:
    """Convert a random named parameters to json string as bytes."""
    key = orjson.dumps(dict(sorted(kwargs.items())))
    logger.info("Search person in cache by key <{0}>".format(str(key)))

    return orjson.dumps(dict(sorted(kwargs.items())))
