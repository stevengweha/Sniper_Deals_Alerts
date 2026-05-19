

WITH base_delays AS (
    SELECT 
        gare_depart,
        AVG(taux_ponctualite) as avg_ponctualite,
        SUM(nb_trains_en_retard) as sum_retards,
        COUNT(*) as nb_observations
    FROM "smart_buy_db"."public_transport"."stg_sncf_delays"
    GROUP BY 1
),

frequentation AS (
    SELECT * FROM "smart_buy_db"."public_transport"."stg_sncf_frequentation"
)

SELECT 
    d.gare_depart,
    ROUND(d.avg_ponctualite::numeric, 2) as ponctualite_moyenne,
    d.sum_retards as total_retards,
    d.nb_observations as nombre_de_trajets_observes,
    f.nb_voyageurs,
    -- Score d'impact : Retards pondérés par le nombre de voyageurs
    ROUND((d.sum_retards::float / NULLIF(f.nb_voyageurs, 0) * 1000)::numeric, 4) as score_nuisance_sociale
FROM base_delays d
LEFT JOIN frequentation f ON d.gare_depart = f.nom_gare
ORDER BY ponctualite_moyenne ASC