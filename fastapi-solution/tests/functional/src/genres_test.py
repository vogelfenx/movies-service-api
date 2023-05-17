import pytest
from http import HTTPStatus

import pytest
import requests


def test_genres(main_api_url):
    url = "{0}/api/v1/genres".format(main_api_url)
    print(url)
    response = requests.get(url)
    assert response.status_code == HTTPStatus.OK
    assert response.json()[0] == {
        "name": "Action",
        "uuid": "3d8d9bf5-0d90-4353-88ba-4ccc5d2c07ff",
    }
