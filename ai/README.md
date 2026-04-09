# Module IA - DemocratIA

## Architecture

Le module IA fournit trois services principaux :

### 1. Summarizer (`ai/services/summarizer.py`)
- Resume les textes parlementaires en 3-5 phrases accessibles
- Prompt optimise pour la vulgarisation legislative
- Supporte le contexte dossier/theme pour des resumes plus precis

### 2. Sentiment Analyzer (`ai/services/sentiment.py`)
- Analyse le sentiment des interventions (favorable/defavorable/neutre)
- Score de confiance 0.0-1.0
- Explication courte en francais du sentiment detecte

### 3. Theme Extractor (`ai/services/theme_extractor.py`)
- Classifie les textes parmi 17 themes parlementaires predefinis
- Extrait les mots-cles associes
- Supporte la classification simple (1 theme) ou multiple (jusqu'a 3)

## Endpoints API

| Endpoint | Methode | Description |
|----------|---------|-------------|
| `/api/ia/resume` | POST | Genere un resume accessible |
| `/api/ia/sentiment` | POST | Analyse le sentiment |

Les deux endpoints verifient le cache avant d'appeler le LLM.

## Cache

Le systeme utilise deux tables de cache PostgreSQL :
- `resume_cache` : stocke les resumes par intervention_id
- `sentiment_cache` : stocke les analyses par (intervention_id, theme)

Le cache est verifie automatiquement avant chaque appel LLM.

## Scripts

### Batch Sentiment (`ai/scripts/batch_sentiment.py`)
Analyse en masse les interventions non traitees :
- Lots de 10 interventions
- Pause de 2 secondes entre les lots
- Statistiques finales (% favorable/defavorable/neutre)

```bash
python ai/scripts/batch_sentiment.py
```

## Modele utilise

- **Modele** : LLM Sonnet (derniere version)
- **Max tokens** : 300-500 selon le service
- **Retry** : 3 tentatives avec backoff exponentiel

## Couts estimes

Pour une base de 10 000 interventions :
- Resumes : ~5M tokens input, ~2.5M tokens output
- Sentiment : ~3M tokens input, ~0.3M tokens output
- Theme : ~3M tokens input, ~0.5M tokens output

Les couts reels dependent de la longueur moyenne des textes.
Le cache reduit les couts en evitant les appels redondants.

## Configuration

Variable d'environnement requise :
```
ANTHROPIC_API_KEY=sk-ant-...
```

Le module fonctionne en mode degrade sans cle API (warnings au demarrage).
