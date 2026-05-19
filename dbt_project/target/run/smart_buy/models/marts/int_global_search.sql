
  
    

  create  table "smart_buy_db"."public"."int_global_search__dbt_tmp"
  
  
    as
  
  (
    

WITH unified AS (
    SELECT * FROM "smart_buy_db"."public"."stg_ebay_data"
    UNION ALL
    SELECT * FROM "smart_buy_db"."public"."stg_leboncoin"
)

SELECT 
    timestamp,
    source,
    title,
    price,
    url,
    -- Calcul d'un prix moyen par source pour la démo
    AVG(price) OVER(PARTITION BY source) as source_avg_price
FROM unified
WHERE price IS NOT NULL
ORDER BY price ASC
  );
  