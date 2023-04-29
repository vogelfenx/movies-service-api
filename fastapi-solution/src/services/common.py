"""This file contains common functions or class for services"""
import orjson


def prepare_key_by_args(**kwargs) -> bytes:
    """Converts a random named parameters to json string as bytes"""
    return orjson.dumps(dict(sorted(kwargs.items())))
