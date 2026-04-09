# DemocratIA - Scrutins endpoint tests

from app.models.scrutin import Scrutin
from app.models.vote import Vote
from app.models.depute import Depute
from app.models.groupe import Groupe


def _seed_scrutin_data(db_session):
    """Seed test data for scrutin tests."""
    groupe = Groupe(id="GP1", nom="Test Groupe", sigle="TG", couleur="#FF0000")
    db_session.add(groupe)

    depute = Depute(
        id="PA001",
        nom="Dupont",
        prenom="Jean",
        groupe_politique_id="GP1",
        departement="Paris",
    )
    db_session.add(depute)

    scrutin = Scrutin(
        id="VTANR001",
        titre="Vote sur le budget 2024",
        date="2024-10-15",
        nb_pour=310,
        nb_contre=245,
        nb_abstention=12,
    )
    db_session.add(scrutin)

    vote = Vote(
        scrutin_id="VTANR001",
        depute_id="PA001",
        position="pour",
    )
    db_session.add(vote)
    db_session.commit()


def test_list_scrutins_returns_200(client):
    response = client.get("/api/scrutins")
    assert response.status_code == 200
    data = response.json()
    assert "items" in data
    assert "total" in data


def test_list_scrutins_with_theme_filter(client, db_session):
    scrutin = Scrutin(
        id="VTANR_FILTER",
        titre="Vote ecologie",
        date="2024-09-01",
        nb_pour=300,
        nb_contre=200,
        nb_abstention=10,
    )
    db_session.add(scrutin)
    db_session.commit()

    response = client.get("/api/scrutins?theme=ecologie")
    assert response.status_code == 200


def test_get_scrutin_not_found(client):
    response = client.get("/api/scrutins/nonexistent")
    assert response.status_code == 404


def test_get_scrutin_with_votes(client, db_session):
    _seed_scrutin_data(db_session)

    response = client.get("/api/scrutins/VTANR001")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == "VTANR001"
    assert data["nb_pour"] == 310
    assert "votes_par_groupe" in data


def test_list_scrutins_pagination(client):
    response = client.get("/api/scrutins?page=1&size=5")
    assert response.status_code == 200
    data = response.json()
    assert data["page"] == 1
    assert data["size"] == 5
