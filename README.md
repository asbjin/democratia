# DemocratIA

Tableau de bord citoyen pour suivre l'activite parlementaire francaise, base sur l'Open Data de l'Assemblee Nationale.

DemocratIA permet aux citoyens de rechercher, visualiser et comprendre l'activite de leurs deputes : interventions, votes, amendements, et plus encore. Un module d'intelligence artificielle propose des resumes accessibles et une analyse de sentiment des debats.

## Equipe

| Nom | Role | Email |
|-----|------|-------|
| Tebti Mohamed Anis | IA / Tech Lead | anis.tebti@democratia.dev |
| Rais Walid | Backend | walid.rais@democratia.dev |
| Aiche Youva | Frontend | youva.aiche@democratia.dev |
| Ceran Mohamed | ETL / Data | mohamed.ceran@democratia.dev |
| Chabla Yassine | DevOps | yassine.chabla@democratia.dev |

## Stack technique

- **Backend** : Python 3.11, FastAPI, SQLAlchemy, Alembic
- **Frontend** : React 18, Vite, Tailwind CSS, Recharts
- **Base de donnees** : PostgreSQL 16 (avec pg_trgm et unaccent)
- **ETL** : Python, requests, SQLAlchemy
- **IA** : LLM API, tenacity
- **Infrastructure** : Docker Compose, Nginx
- **Donnees** : Open Data Assemblee Nationale (https://data.assemblee-nationale.fr/)

## Demarrage rapide

1. Cloner le depot :
   ```bash
   git clone https://github.com/votre-org/democratia.git
   cd democratia
   ```

2. Copier le fichier d'environnement :
   ```bash
   cp .env.example .env
   ```

3. Modifier `.env` avec vos propres valeurs (cle API LLM, etc.)

4. Lancer les services :
   ```bash
   make up
   ```

5. Charger les donnees parlementaires :
   ```bash
   make etl
   ```

6. Acceder a l'application :
   - Frontend : http://localhost
   - API : http://localhost:8000/api/health
   - API docs : http://localhost:8000/docs

## Commandes utiles

```bash
make up        # Demarrer les services
make down      # Arreter les services
make logs      # Voir les logs
make test      # Lancer les tests
make etl       # Lancer le pipeline ETL
make migrate   # Appliquer les migrations
make clean     # Tout nettoyer (volumes inclus)
```

## Licence

Projet universitaire - Tous droits reserves.
