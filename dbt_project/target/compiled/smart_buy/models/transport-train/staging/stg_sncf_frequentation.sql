

WITH unpivoted AS (
    
    SELECT 
        TRIM(UPPER("nom_gare")) as nom_gare,
        2015 as annee,
        
            CAST("total_voyageurs_2015" AS INT) 
         as nb_voyageurs,
        "segmentation_marketing"
    FROM "smart_buy_db"."public"."raw_sncf_frequentation"
     UNION ALL 
    
    SELECT 
        TRIM(UPPER("nom_gare")) as nom_gare,
        2016 as annee,
        
            CAST("total_voyageurs_2016" AS INT) 
         as nb_voyageurs,
        "segmentation_marketing"
    FROM "smart_buy_db"."public"."raw_sncf_frequentation"
     UNION ALL 
    
    SELECT 
        TRIM(UPPER("nom_gare")) as nom_gare,
        2017 as annee,
         
            CAST("totalvoyageurs2017" AS INT) 
         as nb_voyageurs,
        "segmentation_marketing"
    FROM "smart_buy_db"."public"."raw_sncf_frequentation"
     UNION ALL 
    
    SELECT 
        TRIM(UPPER("nom_gare")) as nom_gare,
        2018 as annee,
        
            CAST("total_voyageurs_2018" AS INT) 
         as nb_voyageurs,
        "segmentation_marketing"
    FROM "smart_buy_db"."public"."raw_sncf_frequentation"
     UNION ALL 
    
    SELECT 
        TRIM(UPPER("nom_gare")) as nom_gare,
        2019 as annee,
        
            CAST("total_voyageurs_2019" AS INT) 
         as nb_voyageurs,
        "segmentation_marketing"
    FROM "smart_buy_db"."public"."raw_sncf_frequentation"
     UNION ALL 
    
    SELECT 
        TRIM(UPPER("nom_gare")) as nom_gare,
        2020 as annee,
        
            CAST("total_voyageurs_2020" AS INT) 
         as nb_voyageurs,
        "segmentation_marketing"
    FROM "smart_buy_db"."public"."raw_sncf_frequentation"
     UNION ALL 
    
    SELECT 
        TRIM(UPPER("nom_gare")) as nom_gare,
        2021 as annee,
        
            CAST("total_voyageurs_2021" AS INT) 
         as nb_voyageurs,
        "segmentation_marketing"
    FROM "smart_buy_db"."public"."raw_sncf_frequentation"
     UNION ALL 
    
    SELECT 
        TRIM(UPPER("nom_gare")) as nom_gare,
        2022 as annee,
        
            CAST("total_voyageurs_2022" AS INT) 
         as nb_voyageurs,
        "segmentation_marketing"
    FROM "smart_buy_db"."public"."raw_sncf_frequentation"
     UNION ALL 
    
    SELECT 
        TRIM(UPPER("nom_gare")) as nom_gare,
        2023 as annee,
        
            CAST("total_voyageurs_2023" AS INT) 
         as nb_voyageurs,
        "segmentation_marketing"
    FROM "smart_buy_db"."public"."raw_sncf_frequentation"
     UNION ALL 
    
    SELECT 
        TRIM(UPPER("nom_gare")) as nom_gare,
        2024 as annee,
        
            CAST("total_voyageurs_2024" AS INT) 
         as nb_voyageurs,
        "segmentation_marketing"
    FROM "smart_buy_db"."public"."raw_sncf_frequentation"
    
    
)
SELECT * FROM unpivoted