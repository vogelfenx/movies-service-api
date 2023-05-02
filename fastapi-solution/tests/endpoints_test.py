from http import HTTPStatus

from fastapi.testclient import TestClient
from src.main import app


def test_genres():
    with TestClient(app) as client:
        response = client.get("/api/v1/genres")
        assert response.status_code == HTTPStatus.OK
        assert response.json()[0] == {
            "name": "Action",
            "uuid": "3d8d9bf5-0d90-4353-88ba-4ccc5d2c07ff",
        }


def test_person_films_count():
    with TestClient(app) as client:
        response = client.get(
            "/api/v1/persons/26e83050-29ef-4163-a99d-b546cac208f8",
        )
        assert response.status_code == HTTPStatus.OK
        assert len(response.json()["films"]) == 14


def test_films():
    with TestClient(app) as client:
        response = client.get(
            "/api/v1/films/0657217e-9efa-48fe-be08-6ca29bcaf042",
        )
        assert response.status_code == HTTPStatus.OK
        assert len(response.json()["actors"]) == 4
        assert response.json()["title"] == "Top Star"
