
  
    

  create  table "smart_buy_db"."public_shopping"."final_data__dbt_tmp"
  
  
    as
  
  (
    

with classified_source as (
    select * from "smart_buy_db"."public_shopping"."int_classified_products"
),

-- 1. Déduplication temporelle
deduplicated as (
    select 
        *,
        row_number() over(
            partition by title, source, search_keyword, sub_category, type, category
            order by timestamp desc
        ) as rank
    from classified_source
),

fresh_data as (
    select 
        timestamp, source, search_keyword, sub_category, title, product_brand, price, etat, url, type, category
    from deduplicated
    where rank = 1 and price > 0
),

-- 2. Profilage statistique à l'échelle de la CATEGORY & ETAT
market_stats as (
    select
        category,
        etat,
        count(*) as market_volume, 
        percentile_cont(0.5) within group (order by price) as median_category_price,
        avg(price) as avg_category_price,
        min(price) as min_category_price,
        max(price) as max_category_price,
        stddev_pop(price) as price_volatility 
    from fresh_data
    group by category, etat
),

-- 3. Calcul du prix de référence par TYPE
type_stats as (
    select
        category,
        type,
        etat,
        percentile_cont(0.5) within group (order by price) as median_type_price
    from fresh_data
    group by category, type, etat
),

-- 4. Enrichissement Mathématique Flawless
analytics_enriched as (
    select
        f.timestamp,
        f.source,
        f.search_keyword,
        f.sub_category,
        f.title,
        f.product_brand,
        f.price,
        f.etat,
        f.type,
        f.category,
        f.url,
        
        m.market_volume,
        m.median_category_price,
        m.avg_category_price,
        m.min_category_price,
        m.max_category_price,
        m.price_volatility,
        t.median_type_price,
        
        -- Z-SCORE (Calculé sur la Category)
        cast((f.price - m.avg_category_price) / nullif(m.price_volatility, 0) as decimal(10,2)) as z_score,
        
        -- Écart en pourcentage (Basé sur son TYPE spécifique)
        cast(((f.price - t.median_type_price) / nullif(t.median_type_price, 0)) * 100 as decimal(10,2)) as pct_deviation,
        
        -- GAIN ESTIMÉ CORRIGÉ
        cast(t.median_type_price - f.price as decimal(10,2)) as estimated_resell_profit,
        
        -- Âge de la donnée
        round(cast(extract(epoch from (current_timestamp - f.timestamp)) / 3600 as decimal(10,1))) as data_age_hours

    from fresh_data f
    left join market_stats m 
        on f.category = m.category 
        and f.etat = m.etat
    left join type_stats t
        on f.category = t.category
        and f.type = t.type
        and f.etat = t.etat
),

-- 5. Machine à Décision (Calcul des labels isolés pour le tri)
decision_machine as (
    select
        timestamp,
        source,
        search_keyword,
        category,
        type,
        sub_category,
        title,
        product_brand,
        price,
        etat,
        url,
        
        market_volume,
        min_category_price as min_market_price,     
        avg_category_price as avg_market_price,
        median_category_price as median_market_price,
        median_type_price, 
        max_category_price as max_market_price,     
        price_volatility,
        
        pct_deviation,
        z_score,
        estimated_resell_profit,
        data_age_hours,
        
        -- CONFIDENCE SCORE
        case
            when market_volume < 5 then '🔴 Faible (Marché mort)'
            when market_volume between 5 and 20 then '🟡 Moyenne'
            else '🟢 Haute (Volume global robuste)'
        end as statistical_confidence,

        -- SCORING AVANCÉ METIER
        case
            when price <= (median_type_price * 0.70) and estimated_resell_profit >= 30.0 and market_volume >= 5 then '💎 ANOMALIE DE MARCHÉ (Flipping très rentable)'
            when price <= (median_type_price * 0.85) and market_volume >= 5 then '🔥 EXCELLENT DEAL'
            when price > (median_type_price * 1.20) then '❌ SURÉVALUÉ'
            else '📊 PRIX DU MARCHÉ'
        end as deal_score,
        
        -- ALERTE SNIPER
        case
            when data_age_hours <= 1 and price <= (median_type_price * 0.85) and market_volume >= 5 then '🚨 SNIPER : ACHETER MAINTENANT !'
            when data_age_hours > 48 then '💤 Obsolète'
            else '🟢 Stable'
        end as operational_status
    from analytics_enriched
)

-- 6. Restitution finale et Tri chirurgical
select * from decision_machine
order by case 
             when deal_score like '💎%' then 1 
             when deal_score like '🔥%' then 2 
             when deal_score like '📊%' then 3 
             else 4 
         end asc, 
         estimated_resell_profit desc, 
         data_age_hours asc
  );
  