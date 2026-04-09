# DemocratIA - Groupes endpoint tests

from app.models.groupe import Groupe
from app.models.depute import Depute


def _seed_groupe_data(db_session):
    """Seed test data for groupe tests."""
    groupe = Groupe(id="GP_TEST", nom="Groupe Test", sigle="GT", couleur="#0000FF")
    db_session.add(groupe)

    for i in range(3):
        depute = Depute(
            id=f"PA_GT_{i}",
            nom=f"Nom{i}",
            prenom=f"Prenom{i}",
            groupe_politique_id="GP_TEST",
            departement="Paris",
        )
        db_session.add(depute)

    db_session.commit()


def test_list_groupes_returns_200(client):
    response = client.get("/api/groupes")
    assert response.status_code == 200
    data = response.json()
    assert "items" in data
    assert "total" in data


def test_list_groupes_with_members(client, db_session):
    _seed_groupe_data(db_session)

    response = client.get("/api/groupes")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] >= 1

    groupe = next((g for g in data["items"] if g["id"] == "GP_TEST"), None)
    assert groupe is not None
    assert groupe["nb_membres"] == 3
    assert groupe["sigle"] == "GT"


def test_get_groupe_not_found(client):
    response = client.get("/api/groupes/nonexistent")
    assert response.status_code == 404


def test_get_groupe_detail(client, db_session):
    _seed_groupe_data(db_session)

    response = client.get("/api/groupes/GP_TEST")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == "GP_TEST"
    assert data["nom"] == "Groupe Test"
    assert data["nb_membres"] == 3
    assert len(data["deputes"]) == 3


def test_get_groupe_dashboard(client, db_session):
    _seed_groupe_data(db_session)

    response = client.get("/api/groupes/GP_TEST/dashboard")
    assert response.status_code == 200
    data = response.json()
    assert "groupe" in data
    assert "stats" in data
    assert "cohesion" in data
    assert "top_deputes" in data
    assert "timeline" in data
    assert data["groupe"]["id"] == "GP_TEST"


def test_get_groupe_dashboard_not_found(client):
    response = client.get("/api/groupes/nonexistent/dashboard")
    assert response.status_code == 404
