"""This file contains common functions or class for services."""
from core.logger import get_logger

logger = get_logger(__name__)


def prepare_key_by_args(**kwargs) -> str:
    """Convert a random named parameters to string as key:value pairs."""
    return ':'.join([f'{key}:{value}' for key, value in kwargs.items()])
