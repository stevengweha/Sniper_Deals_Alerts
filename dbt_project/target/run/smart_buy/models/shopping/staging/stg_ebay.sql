
  
    

  create  table "smart_buy_db"."public_shopping"."stg_ebay__dbt_tmp"
  
  
    as
  
  (
    SELECT
    ingested_at AS timestamp,
    'ebay' AS source,
    search_keyword,
    title,
    CAST(NULL AS TEXT) AS product_brand,
    CAST(
        NULLIF(
            REGEXP_REPLACE(
                -- 1. On ne garde QUE les chiffres et le point/virgule
                REGEXP_REPLACE(price_raw, '[^0-9,.]', '', 'g'),
                -- 2. On gère le format : si la virgule est à 2 chiffres de la fin, c'est une décimale
                -- Sinon (si elle est avant), c'est un séparateur de milliers qu'on supprime
                ',(?=[0-9]{2}$)', '.' 
            ),
            ''
        ) AS DOUBLE PRECISION
    ) AS price,
    CASE 
        WHEN LOWER(etat) LIKE '%neuf%' THEN 'Neuf'
        WHEN LOWER(etat) LIKE '%excellent%' THEN 'Excellent état'
        WHEN LOWER(etat) LIKE '%tres bon%' OR LOWER(etat) LIKE '%très bon%' THEN 'Très bon état'
        ELSE 'Occasion'
    END AS etat,
    url
FROM "smart_buy_db"."public"."raw_ebay"
WHERE price_raw ~ '[0-9]'
  );
  