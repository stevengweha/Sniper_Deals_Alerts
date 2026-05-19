SELECT 
    annee,
    gare_depart,
    segmentation_marketing,
    AVG(taux_ponctualite) as ponctualite_annuelle,
    SUM(nb_trains_retard_arrivee) as total_retards_an,
    MAX(nb_voyageurs) as flux_voyageurs,
    AVG(score_nuisance) as indice_nuisance_moyen,
    cause_principale,
    statut_ligne
FROM "smart_buy_db"."public_transport"."int_transport_performance"
GROUP BY 1, 2, 3, 8, 9
ORDER BY annee DESC, indice_nuisance_moyen DESC