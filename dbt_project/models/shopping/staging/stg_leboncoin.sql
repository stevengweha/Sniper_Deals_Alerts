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
    FROM {{ source('raw_data', 'raw_leboncoin') }}
    WHERE title IS NOT NULL
      AND price_cleaned IS NOT NULL 
      AND price_cleaned > 0
)

SELECT
    timestamp,
    ingested_at,
    source_name AS source, -- 🟢 Maintenant "source_name" existe bien car on lit depuis "source_data" !
    category,
    brand,
    title,
    price,
    'Occasion' AS product_condition,
    url
FROM source_data -- 👈 C'est ici qu'était le bug ! On appelle la CTE, pas la source brute