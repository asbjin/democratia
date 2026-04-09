# DemocratIA - Parliamentary synonym dictionary

# Maps a search term to related terms used in parliamentary debate
SYNONYMS: dict[str, list[str]] = {
    # Environment
    "climat": ["environnement", "ecologie", "transition energetique", "rechauffement", "carbone"],
    "environnement": ["climat", "ecologie", "biodiversite", "pollution", "developpement durable"],
    "ecologie": ["environnement", "climat", "biodiversite", "transition", "vert"],
    # Housing
    "logement": ["habitat", "HLM", "hebergement", "immobilier", "locataire", "proprietaire"],
    "habitat": ["logement", "HLM", "urbanisme", "renovation", "construction"],
    # Health
    "sante": ["hopital", "medecin", "soins", "medicament", "CPAM", "Secu"],
    "hopital": ["sante", "urgences", "soins", "clinique", "personnel soignant"],
    # Education
    "education": ["ecole", "enseignement", "professeur", "eleve", "formation"],
    "ecole": ["education", "enseignement", "primaire", "college", "lycee"],
    # Employment
    "emploi": ["travail", "chomage", "entreprise", "salaire", "formation"],
    "travail": ["emploi", "salarie", "droit du travail", "conditions", "temps de travail"],
    "chomage": ["emploi", "pole emploi", "demandeur d'emploi", "insertion"],
    # Security
    "securite": ["police", "gendarmerie", "delinquance", "justice", "terrorisme"],
    "police": ["securite", "gendarmerie", "forces de l'ordre", "maintien de l'ordre"],
    # Immigration
    "immigration": ["migrant", "asile", "etranger", "integration", "frontiere"],
    "asile": ["refugie", "immigration", "protection", "demandeur", "OFPRA"],
    # Budget
    "budget": ["finances", "impot", "fiscalite", "dette", "depenses publiques"],
    "impot": ["fiscalite", "taxe", "budget", "prelevement", "contribution"],
    "fiscalite": ["impot", "taxe", "TVA", "budget", "recettes"],
    # Retirement
    "retraite": ["pension", "age de depart", "cotisation", "regime", "penibilite"],
    "pension": ["retraite", "minimum contributif", "regime", "caisse"],
    # Justice
    "justice": ["tribunal", "magistrat", "penal", "civil", "droit"],
    # Transport
    "transport": ["mobilite", "SNCF", "route", "autoroute", "ferroviaire", "velo"],
    "mobilite": ["transport", "deplacement", "accessibilite", "infrastructure"],
    # Agriculture
    "agriculture": ["agriculteur", "PAC", "exploitation", "alimentation", "rural"],
    "alimentation": ["agriculture", "nourriture", "agroalimentaire", "bio", "qualite"],
    # Numerique
    "numerique": ["digital", "internet", "donnees", "cybersecurite", "intelligence artificielle"],
    "cybersecurite": ["numerique", "piratage", "donnees", "protection", "ANSSI"],
    # Europe
    "europe": ["europeen", "UE", "Bruxelles", "directive", "commission"],
    # Outre-mer
    "outre-mer": ["DOM-TOM", "Guadeloupe", "Martinique", "Reunion", "Guyane", "Mayotte"],
    # Collectivites
    "commune": ["collectivite", "maire", "conseil municipal", "intercommunalite"],
    "collectivite": ["commune", "departement", "region", "decentralisation"],
}


def expand_query(query: str) -> list[str]:
    """Expand a search query with synonyms.

    Args:
        query: The original search query.

    Returns:
        List of expanded terms (original + synonyms).
    """
    terms = [query]
    query_lower = query.lower().strip()

    for key, synonyms in SYNONYMS.items():
        if key in query_lower:
            terms.extend(synonyms)
            break

    # Deduplicate while preserving order
    seen = set()
    unique = []
    for t in terms:
        if t.lower() not in seen:
            seen.add(t.lower())
            unique.append(t)

    return unique


def get_tsquery_expanded(query: str) -> str:
    """Build an expanded PostgreSQL ts_query string.

    Args:
        query: The original search query.

    Returns:
        A ts_query-compatible string with synonyms OR'd together.
    """
    expanded = expand_query(query)
    # Join with OR operator for full-text search
    return " | ".join(expanded)
