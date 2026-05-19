
  
    

  create  table "smart_buy_db"."public_shopping"."int_global_search__dbt_tmp"
  
  
    as
  
  (
    

WITH unified AS (
    SELECT * FROM "smart_buy_db"."public_shopping"."stg_ebay"
    UNION ALL
    SELECT * FROM "smart_buy_db"."public_shopping"."stg_leboncoin"
),

deduplicated AS (
    SELECT 
        *,
        ROW_NUMBER() OVER(
            PARTITION BY title, source, search_keyword 
            ORDER BY timestamp DESC
        ) as rank
    FROM unified
)

SELECT 
    timestamp,
    source,
    search_keyword,
    title,
    price,
    url,
    -- Ton KPI de comparaison
    AVG(price) OVER(PARTITION BY search_keyword) as avg_market_price
FROM deduplicated
WHERE rank = 1 
  AND price > 0
ORDER BY search_keyword, price ASC
  );
  