import os

import pytest

pytest_plugins = ["docker_compose"]


@pytest.fixture(scope="module")
def docker_compose_file(pytestconfig):
    """Config docker-compose for pytest."""
    return os.path.join(str(pytestconfig.rootdir), "docker-compose.test.yaml")
