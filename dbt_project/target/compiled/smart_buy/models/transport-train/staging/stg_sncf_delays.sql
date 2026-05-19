SELECT
    -- On ne cast que si ça ressemble à une date (YYYY-MM)
    CAST("Date" || '-01' AS DATE) as date_mois, 
    "Service" as type_service,
    "Gare de départ" as gare_depart,
    "Gare d'arrivée" as gare_arrivee,
    
    CAST("Nombre de circulations prévues" AS INT) as nb_trains_prevus,
    CAST("Nombre de circulations prévues" AS INT) - CAST("Nombre de trains annulés" AS INT) as nb_trains_reels,
    CAST("Nombre de trains en retard à l'arrivée" AS INT) as nb_trains_en_retard,
    
    ROUND(
        (100 - (CAST("Nombre de trains en retard à l'arrivée" AS NUMERIC) / 
        NULLIF(CAST("Nombre de circulations prévues" AS INT) - CAST("Nombre de trains annulés" AS INT), 0) * 100))::NUMERIC
    , 2) as taux_ponctualite

FROM "smart_buy_db"."public"."raw_sncf_regularite"
-- On ne prend que les lignes où la date est au bon format
WHERE "Date" ~ '^\d{4}-\d{2}$'