
  create view "smart_buy_db"."public"."stg_ebay_data__dbt_tmp"
    
    
  as (
    SELECT
    timestamp,
    'ebay' AS source,
    title,
    CAST(REPLACE(REGEXP_REPLACE(price_raw, '[^0-9\.,]', '', 'g'), ',', '.') AS FLOAT) AS price,
    NULL AS url
FROM "smart_buy_db"."public"."raw_ebay"
  );