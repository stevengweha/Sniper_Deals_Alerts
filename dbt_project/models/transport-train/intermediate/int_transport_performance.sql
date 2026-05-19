WITH delays AS (SELECT * FROM {{ ref('stg_sncf_regularite') }}),
freq AS (SELECT * FROM {{ ref('stg_sncf_frequentation') }})

SELECT 
    d.*,
    f.nb_voyageurs,
    f.segmentation_marketing,
    -- ENRICHISSEMENT 1 : Score de nuisance (Retards par rapport au flux)
    ROUND((d.nb_trains_retard_arrivee::float / NULLIF(f.nb_voyageurs, 0) * 1000)::numeric, 4) as score_nuisance,
    -- ENRICHISSEMENT 2 : Cause dominante
    CASE 
        WHEN d.prct_externe > GREATEST(d.prct_infra, d.prct_materiel) THEN 'Météo/Externe'
        WHEN d.prct_infra > GREATEST(d.prct_externe, d.prct_materiel) THEN 'Infrastructure'
        ELSE 'SNCF (Matériel/Trafic)'
    END as cause_principale,
    -- ENRICHISSEMENT 3 : Statut visuel pour Streamlit
    CASE 
        WHEN d.taux_ponctualite < 85 THEN '🚨 CRITIQUE'
        WHEN d.taux_ponctualite < 92 THEN '⚠️ MOYEN'
        ELSE '✅ BON'
    END as statut_ligne
FROM delays d
INNER JOIN freq f ON d.gare_depart = f.nom_gare AND d.annee = f.annee