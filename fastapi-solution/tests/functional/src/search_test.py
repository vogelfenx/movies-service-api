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


def test_person_films_count(main_api_url):
    url = "{0}/api/v1/persons/26e83050-29ef-4163-a99d-b546cac208f8".format(
        main_api_url
    )
    response = requests.get(url)
    assert response.status_code == HTTPStatus.OK
    assert len(response.json()["films"]) == 14


def test_films(main_api_url):
    url = "{0}/api/v1/films/0657217e-9efa-48fe-be08-6ca29bcaf042".format(
        main_api_url
    )

    response = requests.get(url)
    assert response.status_code == HTTPStatus.OK
    assert len(response.json()["actors"]) == 4
    assert response.json()["title"] == "Top Star"
