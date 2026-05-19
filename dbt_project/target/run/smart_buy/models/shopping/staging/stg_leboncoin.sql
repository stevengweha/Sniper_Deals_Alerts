
  
    

  create  table "smart_buy_db"."public_shopping"."stg_leboncoin__dbt_tmp"
  
  
    as
  
  (
    SELECT
    ingested_at AS timestamp,
    'leboncoin' AS source,
    search_keyword,
    title,
    CAST(NULL AS TEXT) AS product_brand,
    CAST(
        NULLIF(
            -- 1. On garde uniquement les chiffres, les points et les virgules
            -- 2. On transforme toutes les virgules en points
            -- 3. On extrait la chaîne de caractères qui ressemble à un nombre décimal 
            -- (ex: 1234.56) en supprimant tout point surnuméraire
            REGEXP_REPLACE(
                REPLACE(
                    REGEXP_REPLACE(price_raw, '[^0-9,.]', '', 'g'), 
                ',', '.'),
                '(?<=\..*)\.', '', 'g' -- Supprime les points supplémentaires après le premier
            ),
            ''
        ) AS DOUBLE PRECISION
    ) AS price,
    'Occasion' AS etat,
    url
FROM "smart_buy_db"."public"."raw_leboncoin"
-- On exclut tout ce qui n'est pas un prix ou une donnée exploitable
WHERE price_raw NOT LIKE 'Annonce à la une%'
  AND price_raw ~ '[0-9]'
  );
  