{{ config(materialized='view') }}

WITH source_data AS (
    SELECT
        CAST(timestamp AS TIMESTAMP) AS timestamp,
        LOWER(TRIM(keyword)) AS search_keyword,
        TRIM(title) AS title,
        CAST(
            NULLIF(
                -- 1. On vire tout ce qui n'est pas chiffre, point ou virgule
                -- 2. On supprime les virgules qui servent de séparateurs de milliers
                -- 3. On remplace le dernier séparateur décimal (si c'est une virgule) par un point
                REGEXP_REPLACE(
                    REPLACE(REGEXP_REPLACE(price_raw, '[^0-9.,]', '', 'g'), ',', ''), 
                    '\.(?=[0-9]{2}$)', '.' 
                ),
                ''
            ) AS DOUBLE PRECISION
        ) AS price,
        TRIM(etat) AS raw_condition,
        TRIM(url) AS url
    FROM {{ source('raw_data', 'raw_cashexpress') }}
    WHERE title IS NOT NULL
      AND price_raw ~ '[0-9]'
)

SELECT
    timestamp,
    'cashexpress' AS source,
    search_keyword,
    title,
    SPLIT_PART(title, ' ', 1) AS product_brand, 
    price,
    CASE 
        WHEN LOWER(raw_condition) LIKE '%neuf%' THEN 'Neuf'
        WHEN LOWER(raw_condition) LIKE '%excellent%' THEN 'Excellent état'
        WHEN LOWER(raw_condition) LIKE '%tres bon%' THEN 'Très bon état'
        ELSE 'Occasion'
    END AS etat,
    url
FROM source_data
WHERE price IS NOT NULL AND price > 0