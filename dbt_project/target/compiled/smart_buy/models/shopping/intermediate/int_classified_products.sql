

with unified_staging as (
    select timestamp, source, search_keyword, title, product_brand, price, etat, url from "smart_buy_db"."public_shopping"."stg_ebay"
    union all
    select timestamp, source, search_keyword, title, product_brand, price, etat, url from "smart_buy_db"."public_shopping"."stg_leboncoin"
    union all
    select timestamp, source, search_keyword, title, product_brand, price, etat, url from "smart_buy_db"."public_shopping"."stg_cashexpress"
),

rules as (
    select * from "smart_buy_db"."public_shopping"."mapping_sub_categories"
),

-- Jointure sémantique avec PRIORITÉ numérique
matched_rules as (
    select
        u.*,
        coalesce(r.target_sub_category, null) as target_sub_category,
        coalesce(r.pattern_type, 'generic') as pattern_type,
        coalesce(r.priority, 99) as priority,
        row_number() over(
            partition by u.title, u.source, u.timestamp, u.price 
            order by coalesce(r.priority, 99) asc
        ) as rule_rank
    from unified_staging u
    left join rules r
        on lower(u.title) like '%' || lower(r.keyword) || '%'
),

-- ÉTAPE 1 : Génération de sub_category
sub_category_generation as (
    select
        timestamp,
        source,
        search_keyword,
        title,
        product_brand,
        price,
        etat,
        url,
        case
            -- ========== LAYER 1: HARDCODED HIGH-PRIORITY PATTERNS ==========
            -- Smartphones par marque (plus spécifique que les accessoires)
            when lower(title) like '%xiaomi%' and lower(title) like '%redmi%' then '📱 Smartphone'
            when lower(title) like '%xiaomi%' then '📱 Smartphone'
            when lower(title) like '%oppo%' then '📱 Smartphone'
            when lower(title) like '%realme%' then '📱 Smartphone'
            when lower(title) like '%nokia%' then '📱 Smartphone'
            when lower(title) like '%honor%' then '📱 Smartphone'
            when lower(title) like '%huawei%' then '📱 Smartphone'
            when lower(title) like '%motorola%' then '📱 Smartphone'
            when lower(title) like '%wiko%' then '📱 Smartphone'
            when lower(title) like '%sony xperia%' then '📱 Smartphone'
            when lower(title) like '%doro%' then '📱 Smartphone'
            when lower(title) like '%logicom%' then '📱 Smartphone'
            when lower(title) like '%polaroid%' then '📱 Smartphone'
            when lower(title) like '%neow%' then '📱 Smartphone'
            when lower(title) like '%c50s%' then '📱 Smartphone'
            when lower(title) like '%poco%' then '📱 Smartphone'
            when lower(title) like '%redmi%' then '📱 Smartphone'
            when lower(title) like '%mi 9%' then '📱 Smartphone'
            when lower(title) like '%mi 11%' then '📱 Smartphone'
            when lower(title) like '%blackview%' then '📱 Smartphone'
            when lower(title) like '%alcatel%' then '📱 Smartphone'
            when lower(title) like '%lg%' and lower(title) like '%k%' then '📱 Smartphone'
            when lower(title) like '%tcl%' then '📱 Smartphone'
            when lower(title) like '%htc%' then '📱 Smartphone'
            when lower(title) like '%zte%' then '📱 Smartphone'
            when lower(title) like '%orange%' then '📱 Smartphone'
            when lower(title) like '%altice%' then '📱 Smartphone'
            when lower(title) like '%doogee%' then '📱 Smartphone'
            when lower(title) like '%danew%' then '📱 Smartphone'
            when lower(title) like '%staraddict%' then '📱 Smartphone'
            when lower(title) like '%crosscall%' then '📱 Smartphone'
            when lower(title) like '%oneplus%' then '📱 Smartphone'
            when lower(title) like '%thomson%' then '📱 Smartphone'
            when lower(title) like '%evertek%' then '📱 Smartphone'
            when lower(title) like '%freeyond%' then '📱 Smartphone'
            when lower(title) like '%google pixel%' then '📱 Smartphone'
            
            -- Consoles spécifiques (avant accessoires)
            when lower(title) like '%nintendo ds lite%' then '🕹️ Console Nintendo DS'
            when lower(title) like '%nintendo ds%' then '🕹️ Console Nintendo DS'
            when lower(title) like '%nintendo 2ds%' then '🕹️ Console Nintendo 2DS'
            when lower(title) like '%nintendo 3ds%' then '🕹️ Console Nintendo 3DS'
            when lower(title) like '%nintendo dsi%' then '🕹️ Console Nintendo DSi'
            when lower(title) like '%nintendo wii%' then '🕹️ Console Nintendo Wii'
            when lower(title) like '%sega megadrive%' or lower(title) like '%mega drive%' then '🕹️ Console Sega'
            when lower(title) like '%sega saturn%' then '🕹️ Console Sega'
            when lower(title) like '%sega dreamcast%' then '🕹️ Console Sega'
            when lower(title) like '%sega master system%' then '🕹️ Console Sega'
            when lower(title) like '%game gear%' then '🕹️ Console Sega'
            when lower(title) like '%colecovision%' then '🕹️ Console Vintage'
            when lower(title) like '%psone%' or lower(title) like '%ps1%' or lower(title) like '%ps 1%' then '🕹️ Console PS1'
            when lower(title) like '%playstation classic%' then '🕹️ Console PS1'
            when lower(title) like '%ps4 fat%' or lower(title) like '%ps4 1to%' then '🕹️ Console PS4'
            when lower(title) like '%playstation 5%' then '🕹️ Console PS5'
            when lower(title) like '%playstation 4%' then '🕹️ Console PS4'
            when lower(title) like '%playstation 3%' then '🕹️ Console PS3'
            when lower(title) like '%playstation 2%' then '🕹️ Console PS2'
            when lower(title) like '%xbox 360%' then '🕹️ Console Xbox'
            when lower(title) like '%arcade%' and lower(title) like '%console%' then '🕹️ Console Arcade'
            when lower(title) like '%my arcade%' then '🕹️ Console Arcade'
            when lower(title) like '%tiger%' and lower(title) like '%console%' then '🕹️ Console Vintage'
            when lower(title) like '%atari%' then '🕹️ Console Atari'
            when lower(title) like '%bingo%' and lower(title) like '%console%' then '🕹️ Console Vintage'
            when lower(title) like '%gameboy%' or lower(title) like '%game boy%' then '🕹️ Console GameBoy'
            when lower(title) like '%gameboy advance%' or lower(title) like '%game boy advance%' or lower(title) like '%gba%' then '🕹️ Console GameBoy'
            when lower(title) like '%gameboy color%' or lower(title) like '%game boy color%' then '🕹️ Console GameBoy'
            when lower(title) like '%nes%' then '🕹️ Console NES'
            when lower(title) like '%snes%' or lower(title) like '%super nintendo%' or lower(title) like '%super famicom%' then '🕹️ Console SNES'
            when lower(title) like '%famicom%' then '🕹️ Console NES'
            when lower(title) like '%n64%' then '🕹️ Console N64'
            when lower(title) like '%neo geo%' then '🕹️ Console Vintage'
            when lower(title) like '%snk%' and lower(title) like '%pocket%' then '🕹️ Console Vintage'
            when lower(title) like '%psp%' then '🕹️ Console PSP'
            when lower(title) like '%acetronic%' then '🕹️ Console Vintage'
            when lower(title) like '%bandai%' and lower(title) like '%console%' then '🕹️ Console Vintage'
            when lower(title) like '%terror house%' then '🕹️ Console Vintage'
            when lower(title) like '%texas instrument%' then '🕹️ Console Vintage'
            when lower(title) like '%parachute%' and lower(title) like '%nintendo%' then '🕹️ Console Vintage'
            when lower(title) like '%anbernic%' then '🕹️ Console Retro'
            when lower(title) like '%rg40xx%' then '🕹️ Console Retro'
            when lower(title) like '%amstrad%' then '🕹️ Console Vintage'
            when lower(title) like '%lansay%' then '🕹️ Console Vintage'
            when lower(title) like '%radicas%' then '🕹️ Console Vintage'
            when lower(title) like '%liftlever%' then '🕹️ Console Vintage'
            when lower(title) like '%mad monkey%' then '🕹️ Console Retro'
            when lower(title) like '%fisher price%' then '🕹️ Console Enfant'
            when lower(title) like '%vtech%' and lower(title) like '%console%' then '🕹️ Console Enfant'
            
            -- Meubles TV (patterns tele)
            when lower(title) like '%console meuble%' or lower(title) like '%console de salon%' or lower(title) like '%console de rangement%' then '🪑 Meuble TV'
            when lower(title) like '%meuble tv%' or lower(title) like '%meuble télé%' then '🪑 Meuble TV'
            when lower(title) like '%bureau%' and lower(title) like '%console%' then '🪑 Meuble TV'
            when lower(title) like '%secrétaire%' and lower(title) like '%console%' then '🪑 Meuble TV'
            when lower(title) like '%coiffeuse%' and lower(title) like '%console%' then '🪑 Meuble TV'
            when lower(title) like '%console en bois%' or lower(title) like '%console teck%' or lower(title) like '%console cannage%' then '🪑 Meuble TV'
            when lower(title) like '%table console%' and lower(title) like '%télé%' then '🪑 Meuble TV'
            when lower(title) like '%meuble%' and lower(title) like '%tv%' then '🪑 Meuble TV'

            -- ========== LAYER 1-SPÉCIFIQUES: PATTERNS TRÈS SPÉCIFIQUES (AVANT LES PATTERNS GÉNÉRAUX) ==========
            -- Jeux vidéo avec noms spécifiques
            when lower(title) like '%anno 1800%' then '💿 Jeu Vidéo'
            when lower(title) like '%planet coaster%' then '💿 Jeu Vidéo'
            when lower(title) like '%planet zoo%' then '💿 Jeu Vidéo'
            
            -- Magazines TV
            when lower(title) like '%tele poche%' or lower(title) like '%télé poche%' then '📰 Magazine Télé'
            when lower(title) like '%tele pif%' or lower(title) like '%télé pif%' then '📰 Magazine Télé'
            when lower(title) like '%tele loisirs%' or lower(title) like '%télé loisirs%' then '📰 Magazine Télé'
            when lower(title) like '%tele star%' or lower(title) like '%télé star%' then '📰 Magazine Télé'
            when lower(title) like '%tele 7 jours%' or lower(title) like '%télé 7 jours%' then '📰 Magazine Télé'
                when lower(title) like '%tele 7%' or lower(title) like '%télé 7%' then '📰 Magazine Télé'
                when lower(title) like '%tele magazine%' or lower(title) like '%télé magazine%' then '📰 Magazine Télé'
                when lower(title) like '%tele revue%' or lower(title) like '%télé revue%' then '📰 Magazine Télé'
            WHEN lower(title) ILIKE '%Télé%' AND lower(title) ILIKE '%Revue%'  AND lower(title) ILIKE '%Magazine%'  THEN '📰 Magazine TV'
            
            -- Accessoires consoles spécifiques (avant pattern PS5/Xbox général)
            when lower(title) like '%telecomande%' or lower(title) like '%télécommande%' then '🎮 Accessoire Console'
            when lower(title) like '%hdmi%' or lower(title) like '%port hdmi%' then '🔧 Service / Réparation'
            
            -- Casques et audio spécifiques
            when lower(title) like '%casque%' and (lower(title) like '%jbl%' or lower(title) like '%filaire%') then '🎧 Casque Gaming'
            
            -- Accessoires consoles rétro
            when lower(title) like '%housse%' and (lower(title) like '%pocket%' or lower(title) like '%taito%' or lower(title) like '%handheld%') then '🎮 Accessoire Console'
            
            -- Jouets enfants
            when lower(title) like '%baby%' and lower(title) like '%smartphone%' then '🧸 Jouet Enfant'
            when lower(title) like '%vtech%' and (lower(title) like '%toy%' or lower(title) like '%jouet%') then '🧸 Jouet Enfant'
                when lower(title) like '%fisher price%' and (lower(title) like '%toy%' or lower(title) like '%jouet%') then '🧸 Jouet Enfant'
                when lower(title) like '%lego%' then '🧸 Jouet Enfant'
                when lower(title) like '%playmobil%' then '🧸 Jouet Enfant'
                when lower(title) like '%poupée%' then '🧸 Jouet Enfant'
                when lower(title) like '%peluche%' then '🧸 Jouet Enfant'
                when lower(title) like '%jouet%' or lower(title) like '%toy%' then '🧸 Jouet Enfant'

            -- Instruments de musique
            when lower(title) like '%guitare%' and (lower(title) like '%electrique%' or lower(title) like '%acoustique%') then '🎸 Instrument'
            when lower(title) like '%piano%' then '🎸 Instrument '
            when lower(title) like '%batterie%' and (lower(title) like '%instrument%' or lower(title) like '%musique%') then '🎸 Instrument '
            when lower(title) like '%violon%' then '🎸 Instrument '
            when lower(title) like '%saxophone%' then '🎸 Instrument '
            when lower(title) like '%flute%' then '🎸 Instrument '
            when lower(title) like '%clarinette%' then '🎸 Instrument '
            when lower(title) like '%harmonica%' then '🎸 Instrument '
            when lower(title) like '%accordéon%' then '🎸 Instrument '

            -- aide pour console extract console sony xperia et smartphone sony
            when lower(title) like '%sony%' and lower(title) like '%xperia%' then '📱 Smartphone'
            when lower(title) like '%sony%' and lower(title) like '%console%' then '🕹️ Console playstation'
            
        
        
             
        -- 4. PRIORITÉ : Tout ce qui est accessoire
        WHEN lower(title) ~* '(pièce|coque|etui|chargeur|cable|brassard|accessoire|pochette|support|vitre|film|Remplacement)' 
         THEN '🔌 Accessoire  tech'



            -- ========== LAYER 1.5: INTERCEPTION DES PACKS & FAUX AMIS ==========
            when search_keyword in ('tele', 'tv') and lower(title) like '%meuble%' and (lower(title) like '%télé%' or lower(title) like '%tv%') then '📺 Pack TV + Meuble'
            when lower(title) like '%big box%' or lower(title) like '%cd-rom%' then '💿 Jeu Vidéo'
            when lower(title) like '%pc engine%' or lower(title) like '%coregrafx%' or lower(title) like '%turbo express%' then '🕹️ Console Retro'
            when lower(title) like '%ordinateur de bord%' or lower(title) like '%tableau de bord%' or lower(title) like '%compteur%' then '🚗 Pièce Automobile'
            when lower(title) like '%msi claw%' or lower(title) like '%steam deck%' or lower(title) like '%rog ally%' then '🕹️ Console Retro'
            
            -- ========== LAYER 2: RULE-BASED MATCHING (CSV) ==========
            when target_sub_category is not null and rule_rank = 1 then target_sub_category
            
            -- ========== LAYER 3: SMART FALLBACKS ET ANTI-POLLUTION ==========
            when lower(title) like '%annonce %' 
              or lower(title) like '%lot %' 
              or lower(title) like '%divers%' 
              or lower(title) like '%a la une%' 
              or lower(title) like '%vide%' 
              or lower(title) like '%vends%' then '📦 Annonce Divers / Lots'
            
            when lower(title) like '%télé loisirs%' or lower(title) like '%tele loisirs%' then '📰 Magazine TV'
            when lower(title) like '%télé poche%' or lower(title) like '%tele poche%' then '📰 Magazine TV'
            when lower(title) like '%télé star%' or lower(title) like '%tele star%' then '📰 Magazine TV'
            when lower(title) like '%télé 7 jours%' or lower(title) like '%tele 7 jours%' then '📰 Magazine TV'
            when lower(title) like '%telecaster%' then '🎸 Instrument Musique'

            when lower(title) like '%jeu%' or lower(title) like '%jeux%' then '💿 Jeu Vidéo'
            when lower(title) like '%accessoire%' or lower(title) like '%accessories%' then '🎮 Accessoire Console'
            when lower(title) like '%telecommande%' or lower(title) like '%télécommande%' then '🎮 Accessoire Console'
            when lower(title) like '%manette%' or lower(title) like '%controller%' then '🎮 Accessoire Console'
            when lower(title) like '%reparation%' or lower(title) like '%réparation%' or lower(title) like '%hdmi%' then '🔧 Service / Réparation'
            when lower(title) like '%boite seule%' or lower(title) like '%boîte seule%' or lower(title) like '%housse%' then '🎮 Accessoire Console'
            
            when lower(title) like '%support%' and lower(title) like '%smartphone%' then '🔌 Accessoire Smartphone'
            when lower(title) like '%étui%' and lower(title) like '%smartphone%' then '🔌 Accessoire Smartphone'
            when lower(title) like '%coque%' and lower(title) like '%smartphone%' then '🔌 Accessoire Smartphone'
            when lower(title) like '%câble%' and lower(title) like '%smartphone%' then '🔌 Accessoire Smartphone'
            when lower(title) like '%chargeur%' and lower(title) like '%smartphone%' then '🔌 Accessoire Smartphone'
            when lower(title) like '%protection%' and lower(title) like '%smartphone%' then '🔌 Accessoire Smartphone'
            when lower(title) like '%objectif%' and lower(title) like '%smartphone%' then '🔌 Accessoire Smartphone'
            when lower(title) like '%lentille%' and lower(title) like '%smartphone%' then '🔌 Accessoire Smartphone'
            when lower(title) like '%enceinte%' and lower(title) like '%smartphone%' then '🔊 Audio / Home Cinéma'
            when lower(title) like '%batterie%' and lower(title) like '%smartphone%' then '🔌 Accessoire Smartphone'
            when lower(title) like '%pour pièces%' and lower(title) like '%smartphone%' then '🔧 Pièces Détachées'
            when lower(title) like '%trepied%' and lower(title) like '%smartphone%' then '🔌 Accessoire Smartphone'
            when lower(title) like '%stabilisateur%' and lower(title) like '%smartphone%' then '🔌 Accessoire Smartphone'
            when lower(title) like '%feiyutech%' then '🔌 Accessoire Smartphone'
            when lower(title) like '%dji%' then '🔌 Accessoire Smartphone'
            When lower(title) like '%gimbal%' then '🔌 Accessoire Smartphone'
            when lower(title) like '%sac%' and lower(title) like '%smartphone%' then '🔌 Accessoire Smartphone'
            when lower(title) like '%Accessoire%' and lower(title) like '%smartphone%' then '🔌 Accessoire Smartphone'
            
            when lower(title) like '%manette%' and (lower(title) like '%console%' or lower(title) like '%wii%' or lower(title) like '%xbox%' or lower(title) like '%playstation%' or lower(title) like '%switch%') then '🎮 Accessoire Console'
            when lower(title) like '%volant%' and (lower(title) like '%console%' or lower(title) like '%wii%' or lower(title) like '%xbox%' or lower(title) like '%playstation%' or lower(title) like '%switch%') then '🎮 Accessoire Console'
            when lower(title) like '%casque%' and (lower(title) like '%console%' or lower(title) like '%wii%' or lower(title) like '%xbox%' or lower(title) like '%playstation%' or lower(title) like '%switch%') then '🎧 Casque Gaming'
            when lower(title) like '%jeux vidéo%' and (lower(title) like '%console%' or lower(title) like '%wii%' or lower(title) like '%xbox%' or lower(title) like '%playstation%' or lower(title) like '%switch%') then '💿 Jeu Vidéo'
            when lower(title) like '%accessoire%' and (lower(title) like '%jeu%' or lower(title) like '%ps%%' or lower(title) like '%console%' or lower(title) like '%playstation%' or lower(title) like '%switch%') then '💿 Jeu Vidéo'
            when lower(title) like '%POCHETTE%' and (lower(title) like '%CONSOLE%' or lower(title) like '%wii%') then '🎮 Accessoire Console'
            when lower(title) like '%everdrive%' then '🎮 Accessoire Console'
            when lower(title) like '%sync strike%' then '🎮 Accessoire Console'
            when lower(title) like '%beyblade%' then '🎮 Accessoire Gaming'

            when lower(title) like '%appareil photo%' and (lower(title) like '%objectif%' or lower(title) like '%lentille%' or lower(title) like '%trépied%' or lower(title) like '%stabilisateur%' or lower(title) like '%sac%' or lower(title) like '%housse%') then '🔌 Accessoire Camera'
            when lower(title) like '%appareil photo%' and (lower(title) like '%sony%' or lower(title) like '%canon%' or lower(title) like '%nikon%' or lower(title) like '%fujifilm%' or lower(title) like '%olympus%' or lower(title) like '%panasonic%') then '🔌 Accessoire Camera'
            
            -- ========== LAYER 4: PRICE-BASED HEURISTICS ==========
            when search_keyword in ('ps5', 'xbox') and price < 120.0 then '🎮 Accessoire non classé ou Jeu'
            when search_keyword = 'switch' and price < 90.0 then '🎮 Accessoire ou Jeu Switch'
            when search_keyword in ('iphone', 'samsung') and price < 70.0 then '🔌 Accessoire / Pièce détachée'
            when search_keyword in ('tele', 'television', 'tv') and price < 35.0 then '🔌 Accessoire / Pièce détachée TV'
            
            -- ========== LAYER 5: SEARCH CONTEXT FALLBACK ==========
            when search_keyword in ('tele', 'television', 'tv') then '📺 Téléviseur'
            when search_keyword in ('ps5', 'ps4', 'xbox', 'switch', 'console') then '🕹️ Console'
            when search_keyword in ('iphone', 'samsung', 'pixel', 'smartphone') then '📱 Smartphone'
            when search_keyword in ('macbook', 'pc', 'laptop') then '💻 Ordinateur'
            
            -- ========== LAYER 6: GENERIC FALLBACK ==========
            else '📦 Autre'
        end as sub_category
    from matched_rules
    where rule_rank = 1 or rule_rank is null
),

-- ÉTAPE 2 : Extraction de category et type
final_classification as (
    select
        timestamp,
        source,
        search_keyword,
        title,
        product_brand,
        price,
        etat,
        url,
        sub_category,
        split_part(sub_category, ' ', 1) || ' ' || split_part(sub_category, ' ', 2) as category,
        coalesce(
            nullif(trim(regexp_replace(sub_category, '^[^ ]+ [^ ]+ ', '')), ''),
            'Standard'
        ) as type
    from sub_category_generation
)

select * from final_classification