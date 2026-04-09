# DemocratIA

Tableau de bord citoyen pour suivre l'activite parlementaire francaise, base sur l'Open Data de l'Assemblee Nationale.

DemocratIA permet aux citoyens de rechercher, visualiser et comprendre l'activite de leurs deputes : interventions, votes, amendements, et plus encore. Un module d'intelligence artificielle propose des resumes accessibles et une analyse de sentiment des debats.

## Architecture

```
Open Data AN  -->  ETL Pipeline  -->  PostgreSQL 16  -->  FastAPI  -->  React 18  -->  Utilisateur
                                          |                  |
                                     Vues materialisees   Module IA
                                                        (LLM API)
```

Voir [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) pour le diagramme Mermaid complet.

## Equipe

| Nom | Role | Email |
|-----|------|-------|
| Tebti Mohamed Anis | IA / Tech Lead | anistebti10@gmail.com |
| Rais Walid | Backend | raiiswalid@gmail.com |
| Aiche Youva | Data / ETL | youvasin02@gmail.com |
| Ceran Mohamed | Frontend | daddy93.ms@gmail.com |
| Chabla Yassine | DevOps | yassinechabla@gmail.com |

## Stack technique

- **Backend** : Python 3.11, FastAPI, SQLAlchemy (sync), psycopg2-binary
- **Frontend** : React 18, Vite, Tailwind CSS, Recharts, React-Leaflet
- **Base de donnees** : PostgreSQL 16 (pg_trgm, unaccent, vues materialisees)
- **ETL** : Python 3.11, requests, zipfile, json, SQLAlchemy
- **IA** : SDK Python Groq, Llama 3.3 70B Versatile
- **Infrastructure** : Docker Compose, Nginx, GitHub Actions CI
- **Donnees** : Open Data Assemblee Nationale (https://data.assemblee-nationale.fr/)

## Demarrage rapide

1. Cloner le depot :
   ```bash
   git clone https://github.com/asbjin/democratia.git
   cd democratia
   ```

2. Configurer l'environnement :
   ```bash
   cp .env.example .env
   # Editer .env avec vos valeurs
   ```

3. Lancer les services :
   ```bash
   make up
   ```

4. Charger les donnees parlementaires :
   ```bash
   make etl
   ```

5. Acceder a l'application :
   - Frontend : http://localhost
   - API : http://localhost:8000/api/health
   - API docs : http://localhost:8000/docs

Pour un deploiement en production, voir [docs/DEPLOYMENT.md](docs/DEPLOYMENT.md).

## Endpoints API

| Methode | Endpoint | Description |
|---------|----------|-------------|
| GET | `/api/health` | Verification de sante |
| GET | `/api/deputes` | Liste paginee des deputes |
| GET | `/api/deputes/{id}` | Detail d'un depute |
| GET | `/api/deputes/{id}/activite` | Activite d'un depute (interventions, votes, amendements) |
| GET | `/api/deputes/{id}/votes` | Historique des votes d'un depute |
| GET | `/api/deputes/nearby` | Deputes d'un departement et limitrophes |
| GET | `/api/scrutins` | Liste paginee des scrutins |
| GET | `/api/scrutins/{id}` | Detail d'un scrutin avec votes par groupe |
| GET | `/api/groupes` | Liste des groupes politiques |
| GET | `/api/groupes/{id}` | Detail d'un groupe avec ses deputes |
| GET | `/api/groupes/{id}/dashboard` | Dashboard d'un groupe (cohesion, top deputes) |
| GET | `/api/dashboard` | Agregations pour le tableau de bord |
| GET | `/api/dashboard/geo` | Donnees geographiques par departement |
| GET | `/api/search` | Recherche full-text dans les interventions |
| GET | `/api/stats` | Statistiques globales de la plateforme |
| POST | `/api/ia/resume` | Generation de resume par IA |
| POST | `/api/ia/sentiment` | Analyse de sentiment par IA |

## Commandes utiles

```bash
make up        # Demarrer les services
make down      # Arreter les services
make logs      # Voir les logs en temps reel
make test      # Lancer les tests (backend + frontend)
make etl       # Pipeline ETL complet (download + parse + import)
make seed      # Charger les donnees de test
make migrate   # Appliquer les migrations
make monitor   # Verification de sante des services
make backup    # Sauvegarde PostgreSQL
make status    # Etat des conteneurs Docker
make clean     # Tout nettoyer (volumes inclus)
```

## Structure du projet

```
democratia/
├── backend/           # API FastAPI (Walid)
│   ├── app/
│   │   ├── models/    # Modeles SQLAlchemy
│   │   ├── routers/   # Endpoints API
│   │   ├── schemas/   # Schemas Pydantic
│   │   └── services/  # Services metier (synonymes)
│   └── tests/         # Tests pytest
├── frontend/          # Application React (Ceran)
│   ├── src/
│   │   ├── components/  # Composants reutilisables
│   │   ├── pages/       # Pages de l'application
│   │   └── services/    # Client API Axios
│   └── public/          # Assets statiques (GeoJSON, photos)
├── etl/               # Pipeline de donnees (Youva)
│   ├── scripts/       # Scripts d'import et parsing
│   └── fixtures/      # Donnees de test
├── ai/                # Module IA (Anis)
│   ├── services/      # Summarizer, Sentiment, Theme
│   └── scripts/       # Batch processing
├── db/                # Scripts SQL (init, vues materialisees)
├── nginx/             # Configuration reverse proxy
├── scripts/           # Scripts utilitaires (git-as, monitor)
├── docs/              # Documentation
└── docker-compose.yml # Orchestration des services
```

## Licence

Projet universitaire 2025 - Tous droits reserves.
