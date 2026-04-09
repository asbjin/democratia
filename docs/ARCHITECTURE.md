# Architecture - DemocratIA

## Diagramme d'architecture

```mermaid
graph LR
    subgraph Sources
        AN[Open Data<br/>Assemblee Nationale]
    end

    subgraph ETL Pipeline
        DL[download.py<br/>Telechargement ZIP]
        PA[parse_acteurs.py]
        PS[parse_scrutins.py]
        PQ[parse_questions.py]
        PAM[parse_amendements.py]
        IA_IMPORT[import_all.py<br/>Orchestrateur]
    end

    subgraph Base de donnees
        PG[(PostgreSQL 16<br/>pg_trgm + unaccent)]
        MV[Vues materialisees<br/>mv_activite_par_theme<br/>mv_timeline]
    end

    subgraph Backend API
        FA[FastAPI<br/>Python 3.11]
        R_HEALTH[/api/health]
        R_DEPUTES[/api/deputes]
        R_SCRUTINS[/api/scrutins]
        R_GROUPES[/api/groupes]
        R_DASHBOARD[/api/dashboard]
        R_SEARCH[/api/search]
        R_IA[/api/ia]
        R_STATS[/api/stats]
        CACHE[Cache TTL 5min]
        RL[Rate Limiter<br/>100 req/min/IP]
    end

    subgraph Module IA
        SUM[Summarizer]
        SENT[Sentiment Analyzer]
        THEME[Theme Extractor]
        SYN[Synonymes<br/>parlementaires]
        LLM[Groq API<br/>Llama 3.3 70B]
    end

    subgraph Frontend
        REACT[React 18 + Vite]
        PAGES[Pages<br/>Home / Dashboard<br/>Depute / Groupes / About]
        CHARTS[Recharts<br/>Bar / Area / Pie]
        MAP[React-Leaflet<br/>Carte departements]
        AI_COMP[AISummary<br/>SentimentBadge]
    end

    subgraph Infrastructure
        NGINX[Nginx<br/>Reverse proxy<br/>HTTPS]
        DOCKER[Docker Compose]
    end

    AN -->|ZIP JSON| DL
    DL --> PA & PS & PQ & PAM
    PA & PS & PQ & PAM --> IA_IMPORT
    IA_IMPORT -->|INSERT| PG
    PG --> MV

    PG --> FA
    MV --> FA
    FA --> R_HEALTH & R_DEPUTES & R_SCRUTINS & R_GROUPES & R_DASHBOARD & R_SEARCH & R_IA & R_STATS
    FA --> CACHE
    FA --> RL

    R_IA --> SUM & SENT
    R_SEARCH --> SYN
    SUM & SENT & THEME --> LLM

    REACT --> PAGES
    PAGES --> CHARTS & MAP & AI_COMP

    NGINX --> FA
    NGINX --> REACT
    DOCKER --> NGINX & FA & REACT & PG

    classDef source fill:#e8f5e9,stroke:#43a047
    classDef etl fill:#fff3e0,stroke:#ef6c00
    classDef db fill:#e3f2fd,stroke:#1565c0
    classDef api fill:#fce4ec,stroke:#c62828
    classDef ia fill:#f3e5f5,stroke:#7b1fa2
    classDef front fill:#e0f7fa,stroke:#00838f
    classDef infra fill:#f5f5f5,stroke:#616161

    class AN source
    class DL,PA,PS,PQ,PAM,IA_IMPORT etl
    class PG,MV db
    class FA,R_HEALTH,R_DEPUTES,R_SCRUTINS,R_GROUPES,R_DASHBOARD,R_SEARCH,R_IA,R_STATS,CACHE,RL api
    class SUM,SENT,THEME,SYN,LLM ia
    class REACT,PAGES,CHARTS,MAP,AI_COMP front
    class NGINX,DOCKER infra
```

## Flux de donnees

1. **ETL** : Les donnees ouvertes de l'AN sont telechargees (ZIP), parsees (JSON), et inserees dans PostgreSQL
2. **Backend** : FastAPI expose les donnees via une API REST avec cache TTL et rate limiting
3. **IA** : Les textes parlementaires sont resumes et analyses par un LLM, avec cache en base
4. **Frontend** : React consomme l'API et affiche les donnees avec graphiques, cartes et composants IA
5. **Nginx** : Reverse proxy qui route `/api/` vers le backend et `/` vers le frontend

## Decisions techniques

| Choix | Raison |
|-------|--------|
| SQLAlchemy sync | Simplicite, pas besoin d'async pour ce volume |
| pg_trgm + unaccent | Recherche full-text en francais sans accents |
| Vues materialisees | Performance des agregations dashboard |
| Cache TTL en memoire | Reduire la charge DB sur les endpoints frequents |
| Rate limiting par IP | Protection contre les abus sans authentification |
| Synonymes parlementaires | Enrichir les recherches avec le vocabulaire AN |
