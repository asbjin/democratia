CREATE EXTENSION IF NOT EXISTS pg_trgm;
CREATE EXTENSION IF NOT EXISTS unaccent;

-- Materialized view: activity per theme (based on dossier themes)
CREATE MATERIALIZED VIEW IF NOT EXISTS mv_activite_par_theme AS
SELECT
    d.theme,
    COUNT(DISTINCT i.depute_id) AS nb_deputes_actifs,
    COUNT(i.id) AS nb_interventions,
    COUNT(DISTINCT s.id) AS nb_scrutins
FROM dossiers d
LEFT JOIN interventions i ON i.dossier_id = d.id
LEFT JOIN scrutins s ON s.dossier_id = d.id
WHERE d.theme IS NOT NULL
GROUP BY d.theme
ORDER BY nb_interventions DESC;

-- Materialized view: monthly activity timeline
CREATE MATERIALIZED VIEW IF NOT EXISTS mv_timeline AS
SELECT
    EXTRACT(YEAR FROM i.date)::int AS annee,
    EXTRACT(MONTH FROM i.date)::int AS mois,
    COUNT(i.id) AS nb_interventions,
    COUNT(DISTINCT i.depute_id) AS nb_deputes_actifs,
    (SELECT COUNT(*) FROM scrutins sc
     WHERE EXTRACT(YEAR FROM sc.date) = EXTRACT(YEAR FROM i.date)
       AND EXTRACT(MONTH FROM sc.date) = EXTRACT(MONTH FROM i.date)
    ) AS nb_scrutins
FROM interventions i
WHERE i.date IS NOT NULL
GROUP BY annee, mois
ORDER BY annee, mois;

-- Indexes for materialized views
CREATE UNIQUE INDEX IF NOT EXISTS idx_mv_activite_theme ON mv_activite_par_theme (theme);
CREATE UNIQUE INDEX IF NOT EXISTS idx_mv_timeline ON mv_timeline (annee, mois);
