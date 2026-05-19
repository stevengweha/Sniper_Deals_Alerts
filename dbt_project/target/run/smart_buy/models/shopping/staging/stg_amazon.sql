
  
    

  create  table "smart_buy_db"."public_shopping"."stg_amazon__dbt_tmp"
  
  
    as
  
  (
    -- models/staging/stg_amazon.sql
SELECT 
    CURRENT_TIMESTAMP as timestamp, 
    'amazon' as source, 
    'test' as title, 
    0.0 as price
LIMIT 0
  );
  