import pytest
from http import HTTPStatus

import pytest
import requests


def test_films(main_api_url):
    url = "{0}/api/v1/films/0657217e-9efa-48fe-be08-6ca29bcaf042".format(
        main_api_url
    )
    response = requests.get(url)
    assert response.status_code == HTTPStatus.OK
    assert len(response.json()["actors"]) == 4
    assert response.json()["title"] == "Top Star"
