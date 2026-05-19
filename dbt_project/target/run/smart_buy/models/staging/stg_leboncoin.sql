
  create view "smart_buy_db"."public"."stg_leboncoin__dbt_tmp"
    
    
  as (
    SELECT
    timestamp,
    'leboncoin' AS source,
    title,
    -- Extraction du prix numérique pour Postgres
    CAST(NULLIF(REGEXP_REPLACE(price_raw, '[^0-9]', '', 'g'), '') AS FLOAT) AS price,
    url
FROM "smart_buy_db"."public"."raw_leboncoin"
  );