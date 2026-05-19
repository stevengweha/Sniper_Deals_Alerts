{% set years = [2015, 2016, 2017, 2018, 2019, 2020, 2021, 2022, 2023, 2024] %}

WITH unpivoted AS (
    {% for year in years %}
    SELECT 
        TRIM(UPPER("nom_gare")) as nom_gare,
        {{ year }} as annee,
        {% if year == 2017 %} 
            CAST("totalvoyageurs2017" AS INT) 
        {% else %}
            CAST("total_voyageurs_{{ year }}" AS INT) 
        {% endif %} as nb_voyageurs,
        "segmentation_marketing"
    FROM {{ source('transport', 'raw_sncf_frequentation') }}
    {% if not loop.last %} UNION ALL {% endif %}
    {% endfor %}
)
SELECT * FROM unpivoted