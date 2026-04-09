# Projet DemocratIA — Mémoire persistante

## Identités Git (IMMUABLE)
1. Tebti Mohamed Anis | anistebti10@gmail.com | IA / Tech Lead
2. Rais Walid | raiiswalid@gmail.com | Backend
3. Aiche Youva | youvasin02@gmail.com | Data / ETL
4. Ceran Mohamed | daddy93.ms@gmail.com | Frontend
5. Chabla Yassine | yassinechabla@gmail.com | DevOps

## Format de commit
git add -A && GIT_AUTHOR_NAME="Nom" GIT_AUTHOR_EMAIL="email" GIT_COMMITTER_NAME="Nom" GIT_COMMITTER_EMAIL="email" git commit -m "message"
Puis : git push origin main

## Règles
- Branche main uniquement. Jamais de branche, PR, ou worktree.
- Mot "Claude" interdit partout sauf imports Python du package anthropic.
- Mot "Anthropic" interdit dans commentaires et docs.
- Email "@democratia.dev" interdit. Utiliser les Gmail ci-dessus.
- Ne jamais inventer de noms ou emails.
- Ne pas recréer un fichier existant. Le modifier.
- Chaque dossier a UN responsable pour les commits :
  backend/ → Walid
  frontend/ → Ceran
  etl/ → Youva
  ai/ → Anis
  docker, CI, tests, scripts, docs → Yassine

## Stack
- Backend : Python 3.11, FastAPI, SQLAlchemy (sync), psycopg2-binary
- Frontend : React 18, Vite, TailwindCSS, Recharts, React-Leaflet, Axios
- ETL : Python 3.11, requests, zipfile, json, SQLAlchemy
- IA : SDK python anthropic, modèle claude-sonnet-4-20250514
- BDD : PostgreSQL 16, pg_trgm, unaccent
- Infra : Docker, Docker Compose, Nginx, GitHub Actions
- Données : https://data.assemblee-nationale.fr/ (JSON dans ZIP, XVIIe législature)

## Fichiers existants
backend/app/main.py, config.py, database.py
backend/app/models/ : depute.py, groupe.py, dossier.py, intervention.py, scrutin.py, vote.py, question.py, amendement.py, ia_cache.py
backend/app/routers/ : health.py, deputes.py, search.py, dashboard.py, scrutins.py, groupes.py, ia.py
backend/app/schemas/ : depute.py, activite.py, scrutin.py, groupe.py
backend/app/services/ : synonyms.py
backend/tests/ : conftest.py, test_health.py, test_deputes.py, test_scrutins.py, test_groupes.py
frontend/src/pages/ : HomePage.jsx, DashboardPage.jsx, DeputePage.jsx, GroupesPage.jsx
frontend/src/components/ : Navbar.jsx, SearchBar.jsx, DeputeCard.jsx, Layout.jsx, StatCard.jsx, ActivityChart.jsx, TimelineChart.jsx, VoteBreakdown.jsx, MapView.jsx, AISummary.jsx, SentimentBadge.jsx
frontend/src/services/api.js
frontend/public/ : departements.geojson, photos/
etl/scripts/ : download.py, parse_acteurs.py, parse_scrutins.py, parse_questions.py, parse_amendements.py, import_all.py, seed_test_data.py, import_geo.py, import_photos.py
etl/fixtures/ : seed_data.json
ai/services/ : summarizer.py, sentiment.py, theme_extractor.py
ai/scripts/ : batch_sentiment.py
ai/config.py, ai/README.md
docker-compose.yml, Makefile, README.md, .gitignore, .env.example
db/init.sql, nginx/nginx.conf, nginx/ssl-setup.sh, scripts/git-as.sh, scripts/monitor.sh
.github/workflows/ci.yml
# Avancement DemocratIA

## Sprint 0 ✅ DONE
- Structure, Docker, Makefile, README, Nginx, scripts
- Commit : Yassine

## Sprint 1 ✅ DONE — Tag v0.1.0
- ETL pipeline download + parse acteurs/scrutins → Commit Youva
- Backend FastAPI models + routers health/deputes/search/dashboard → Commit Walid
- Frontend React pages Home/Dashboard/Depute + composants → Commit Ceran
- Module IA summarizer + sentiment → Commit Anis
- Cleanup gitignore → Commit Yassine

## Sprint 2 ✅ DONE — Tag v0.2.0
1. ✅ Corriger emails dans git-as.sh → Yassine
2. ✅ Supprimer mentions dans commentaires/docs → Yassine
3. ✅ Backend : routers scrutins.py, groupes.py + enrichir deputes.py → Walid
4. ✅ Frontend : StatCard, ActivityChart, TimelineChart, VoteBreakdown + DashboardPage → Ceran
5. ✅ ETL : parse_questions.py, parse_amendements.py + import_all.py → Youva
6. ✅ Backend IA : routers/ia.py + models/ia_cache.py → Anis
7. ✅ Tests : tests/ + .github/workflows/ci.yml → Yassine
8. ✅ Tag v0.2.0

## Sprint 3 ✅ DONE — Tag v0.3.0
1. ✅ Page depute complete avec 4 onglets + indicateurs → Ceran
2. ✅ Loading states et error handling DashboardPage → Ceran
3. ✅ Vues materialisees mv_activite_par_theme et mv_timeline + cache TTL 5min → Walid
4. ✅ Donnees de test fixtures (50 deputes, 5 groupes, 30 scrutins, 200 interventions) → Youva
5. ✅ Amelioration prompts parlementaires + theme_extractor.py → Anis
6. ✅ ssl-setup.sh + healthchecks Docker + make seed → Yassine

## Sprint 4 ✅ DONE — Tag v0.4.0
1. ✅ Carte Leaflet interactive avec filtrage departement → Ceran
2. ✅ GET /api/dashboard/geo + GET /api/deputes/nearby → Walid
3. ✅ import_geo.py + departements.geojson → Youva
4. ✅ batch_sentiment.py (lots de 10, stats finales) → Anis
5. ✅ monitor.sh + make monitor → Yassine

## Sprint 5 ✅ DONE — Tag v0.5.0
1. ✅ AISummary.jsx + SentimentBadge.jsx + integration DeputePage → Ceran
2. ✅ GroupesPage.jsx + route /groupes + lien Navbar → Ceran
3. ✅ Synonymes parlementaires + enrichissement search.py → Anis
4. ✅ GET /api/groupes/{id}/dashboard (cohesion, top deputes, timeline) → Walid
5. ✅ import_photos.py + comptes rendus dans download.py → Youva
6. ✅ test_scrutins.py + test_groupes.py → Yassine

## Sprint 6 ✅ DONE — Tag v1.0.0
1. ✅ docs/DEPLOYMENT.md + docs/ARCHITECTURE.md + README.md complet → Yassine
2. ✅ Dark mode (prefers-color-scheme + toggle) + responsive + AboutPage → Ceran
3. ✅ Rate limiting 100/min/IP + CORS restrictif + logging structure → Walid
4. ✅ backup.sh + make backup + stats globales import_all.py → Youva
5. ✅ GET /api/stats + demo_themes.json → Anis
6. ✅ Headers DemocratIA sur tous les fichiers Python + nettoyage final → Yassine

## NOTES IMPORTANTES
- Sprints 0-6 : TOUS TERMINÉS - Release v1.0.0
- Le projet n'a PAS besoin de tourner réellement, juste du code propre sur GitHub
- Pas besoin de clé API, pas besoin de Docker lancé
- Le code doit être syntaxiquement correct et cohérent entre les fichiers
