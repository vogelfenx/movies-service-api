import pytest
from http import HTTPStatus

import pytest
import requests


def test_person_films_count(main_api_url):
    url = "{0}/api/v1/persons/26e83050-29ef-4163-a99d-b546cac208f8".format(
        main_api_url
    )
    response = requests.get(url)
    assert response.status_code == HTTPStatus.OK
    assert len(response.json()["films"]) == 14
