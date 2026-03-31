"""Tests for deputes endpoint."""


def test_list_deputes_returns_200(client):
    response = client.get("/api/deputes")
    assert response.status_code == 200
    data = response.json()
    assert "items" in data
    assert isinstance(data["items"], list)
    assert "total" in data


def test_list_deputes_with_pagination(client):
    response = client.get("/api/deputes?page=1&size=10")
    assert response.status_code == 200
    data = response.json()
    assert data["page"] == 1
    assert data["size"] == 10


def test_get_depute_not_found(client):
    response = client.get("/api/deputes/nonexistent")
    assert response.status_code == 404
