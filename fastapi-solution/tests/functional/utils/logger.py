import logging

logging.basicConfig()


def get_logger(name: str):
    """Return default logger."""
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    return logger
