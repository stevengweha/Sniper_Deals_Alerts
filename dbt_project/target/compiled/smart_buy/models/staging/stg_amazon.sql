-- models/staging/stg_amazon.sql
SELECT 
    CURRENT_TIMESTAMP as timestamp, 
    'amazon' as source, 
    'test' as title, 
    0.0 as price
LIMIT 0