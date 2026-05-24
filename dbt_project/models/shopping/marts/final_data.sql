{{ config(materialized='table') }}

with classified_source as (
    -- On pointe vers la table intermédiaire
    select * from {{ ref('int_classified_products') }}
),

-- 1. Déduplication temporelle (Sécurisée par l'URL)
deduplicated as (
    select 
        *,
        row_number() over(
            partition by url 
            order by timestamp desc
        ) as rank
    from classified_source
),

fresh_data as (
    select *
    from deduplicated
    where rank = 1 and price > 0
),

-- 2. Profilage MACRO : Statistiques globales par Catégorie et État
macro_stats as (
    select
        category,
        product_condition,
        count(*) as category_volume, 
        avg(price) as avg_category_price
    from fresh_data
    group by category, product_condition
),

-- 3. Profilage MICRO : Prix de référence par Modèle Exact (Sans distinction de capacité)
model_stats as (
    select
        category,
        product_model,
        product_condition,
        count(*) as model_volume,
        percentile_cont(0.5) within group (order by price) as median_model_price,
        avg(price) as avg_model_price,
        stddev_pop(price) as model_price_volatility 
    from fresh_data
    where product_model != 'Modèle non répertorié'
    group by category, product_model, product_condition
),

-- 4. Enrichissement Mathématique (Calculs basés strictement sur le modèle global)
analytics_enriched as (
    select
        f.product_id,
        f.timestamp,
        f.source,
        f.category,
        f.brand,
        f.product_model,
        f.storage_capacity, -- Conservé pour affichage informatif dans le dashboard
        f.screen_size,      -- Conservé pour affichage informatif dans le dashboard
        f.title,
        f.price,
        f.product_condition,
        f.url,
        
        -- Données Macro
        mac.category_volume,
        
        -- Données Micro (Spécifiques au modèle global, ex: iPhone 15 peu importe le stockage)
        coalesce(mic.model_volume, 0) as model_volume,
        mic.median_model_price,
        mic.avg_model_price,
        mic.model_price_volatility,
        
        -- Z-SCORE (Calculé sur la volatilité globale du modèle)
        cast((f.price - mic.avg_model_price) / nullif(mic.model_price_volatility, 0) as decimal(10,2)) as z_score,
        
        -- Écart en pourcentage
        cast(((f.price - mic.median_model_price) / nullif(mic.median_model_price, 0)) * 100 as decimal(10,2)) as pct_deviation,
        
        -- GAIN ESTIMÉ CORRIGÉ (Comparé au prix médian du modèle)
        cast(mic.median_model_price - f.price as decimal(10,2)) as estimated_resell_profit,
        
        -- Âge de la donnée en heures
        round(cast(extract(epoch from (current_timestamp - f.timestamp)) / 3600 as decimal(10,1))) as data_age_hours

    from fresh_data f
    left join macro_stats mac 
        on f.category = mac.category 
        and f.product_condition = mac.product_condition
    left join model_stats mic
        on f.category = mic.category
        and f.product_model = mic.product_model
        and f.product_condition = mic.product_condition
),

-- 5. Machine à Décision (Calcul des labels isolés pour le tri)
decision_machine as (
    select
        product_id,
        timestamp,
        source,
        category,
        brand,
        product_model,
        storage_capacity,
        screen_size,
        title,
        price,
        product_condition,
        url,
        category_volume,
        model_volume,
        median_model_price,
        avg_model_price,
        model_price_volatility,
        z_score,
        pct_deviation,
        estimated_resell_profit,
        data_age_hours,
        
        -- CONFIDENCE SCORE (Fiabilité statistique basée sur la masse critique du modèle)
        CASE
            WHEN product_model = 'Modèle non répertorié' THEN '⚪ Inconnu (Modèle non configuré)'
            WHEN model_volume < 3                       THEN '🔴 Faible (Marché de niche / Risqué)'
            WHEN model_volume BETWEEN 3 AND 10          THEN '🟡 Moyenne (Volume modéré)'
            ELSE                                             '🟢 Élevée (Masse critique / Liquide)'
        END AS statistical_confidence,

        -- SCORING AVANCÉ METIER
        case
            when product_model != 'Modèle non répertorié' 
                 and price <= (median_model_price * 0.75) 
                 and estimated_resell_profit >= 40.0 
                 and model_volume >= 3 
            then '💎 EXCELLENT DEAL (Flipping très rentable)'
            
            when product_model != 'Modèle non répertorié'
                 and price <= (median_model_price * 0.85) 
                 and model_volume >= 3 
            then '🔥 BON DEAL'
            
            when price > (median_model_price * 1.15) 
            then '❌ SURÉVALUÉ'
            
            else '📊 PRIX DU MARCHÉ '
        end as deal_score,
        
        -- ALERTE SNIPER
        case
            when data_age_hours <= 2 
                 and price <= (median_model_price * 0.85) 
                 and model_volume >= 3 
            then '🚨 SNIPER : ACHETER MAINTENANT !'
            when data_age_hours > 72 then '💤 Obsolète'
            else '🟢 Actif'
        end as operational_status
        
    from analytics_enriched
)

-- 6. Restitution finale et Tri chirurgical
select * from decision_machine
order by 
    case 
         when deal_score like '💎%' then 1 
         when deal_score like '🔥%' then 2 
         when deal_score like '📊%' then 3 
         else 4 
    end asc, 
    estimated_resell_profit desc nulls last, 
    data_age_hours asc