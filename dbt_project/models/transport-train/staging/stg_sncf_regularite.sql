SELECT
    CAST("Date" || '-01' AS DATE) as date_mois,
    CAST(LEFT("Date", 4) AS INT) as annee,
    "Service" as type_service,
    TRIM(UPPER("Gare de départ")) as gare_depart,
    TRIM(UPPER("Gare d'arrivée")) as gare_arrivee,
    CAST("Nombre de circulations prévues" AS INT) as nb_trains_prevus,
    COALESCE(CAST("Nombre de trains annulés" AS INT), 0) as nb_trains_annules,
    CAST("Nombre de trains en retard à l'arrivée" AS INT) as nb_trains_retard_arrivee,
    -- Calcul de la ponctualité
    ROUND(
        (100 - (CAST("Nombre de trains en retard à l'arrivée" AS NUMERIC) / 
        NULLIF(CAST("Nombre de circulations prévues" AS INT) - CAST("Nombre de trains annulés" AS INT), 0) * 100))::NUMERIC
    , 2) as taux_ponctualite,
    -- Causes de retards (Enrichissement de base)
    CAST("Prct retard pour causes externes" AS FLOAT) as prct_externe,
    CAST("Prct retard pour cause infrastructure" AS FLOAT) as prct_infra,
    CAST("Prct retard pour cause matériel roulant" AS FLOAT) as prct_materiel
FROM {{ source('transport', 'raw_sncf_regularite') }}
WHERE "Date" ~ '^\d{4}-\d{2}$'