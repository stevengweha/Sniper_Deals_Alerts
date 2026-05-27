{{ config(materialized='view') }}

WITH source_data AS (
    SELECT
        timestamp,
        ingested_at,
        LOWER(TRIM(source)) AS source_name,
        LOWER(TRIM(category)) AS category,
        LOWER(TRIM(brand)) AS brand,
        TRIM(title) AS title,
        price_cleaned AS price,
        TRIM(url) AS url
    FROM {{ source('raw_data', 'raw_ebay') }}
    WHERE title IS NOT NULL
      AND price_cleaned IS NOT NULL 
      AND price_cleaned > 0
)

SELECT
    timestamp,
    ingested_at,
    source_name AS source, 
    category,
    brand,
    title,
    price,
    'Occasion' AS product_condition, 
    url
FROM source_data 