{{ config(materialized='view') }}

WITH unified_staging AS (
    SELECT * FROM {{ ref('stg_cashexpress') }}
    UNION ALL
    SELECT * FROM {{ ref('stg_leboncoin') }}
    UNION ALL
    SELECT * FROM {{ ref('stg_ebay') }}
),

-- ====================================================================
-- 1. ÉTAPE INTERMÉDIAIRE : REDRESSEMENT DES MARQUES ET CATÉGORIES
-- ====================================================================
refined_base AS (
    SELECT
        timestamp,
        ingested_at,
        source,
        title,
        price,
        product_condition,
        url,
        UPPER(category) AS raw_category,
        UPPER(brand) AS raw_brand,

        -- A. Redressement strict de la marque (Nettoyage des erreurs de saisie type Wii chez Sony)
        CASE 
            WHEN UPPER(title) ~* '(IPHONE|APPLE|MACBOOK|AIRPOD)' THEN 'APPLE'
            WHEN UPPER(title) ~* '(GALAXY|SAMSUNG)' THEN 'SAMSUNG'
            WHEN UPPER(title) ~* '(PLAYSTATION|PLAY\s+STATION|PS5|PS4|PS3|PS2|PS1|PSP|SONY)' THEN 'SONY'
            WHEN UPPER(title) ~* '(NINTENDO|SWITCH|WII)' THEN 'NINTENDO'
            WHEN UPPER(title) ~* '(XBOX|MICROSOFT)' THEN 'MICROSOFT'
            WHEN UPPER(title) ~* 'THRUSTMASTER' THEN 'THRUSTMASTER'
            WHEN UPPER(title) ~* 'LOGITECH' THEN 'LOGITECH'
            ELSE UPPER(brand)
        END AS refined_brand,

        -- B. Redressement de la catégorie basé sur le contenu réel de l'annonce
        CASE 
            -- Pièces détachées pures
            WHEN UPPER(title) ~* '(NAPPE|CHASSIS|CHÂSSIS|CARTE MERE|CARTE MÈRE|PIECE|PIÈCE|COMPOSANT|OBJECTIF|TIROIR|VITRE|LECTEUR.*SIM|ANTENNE|MODULE|HAUT PARLEUR|CAMERA|CAMÉRA|CONNECTEUR|POUR PIECE|POUR PIÈCE|ECRAN|ÉCRAN|CHERCHE TOUR| APPAREIL PHOTO ARRIERE|APPAREIL PHOTO ARRIÈRE|BATTERIE IPHONE 17 |CAPTEUR)' 
                 AND NOT UPPER(title) ~* '(RECONDITIONNÉ|DEBLOQUÉ|DÉBLOQUÉ|16GO|32GO|64GO|128GO|256GO|512GO|GIGA)'
                THEN 'PIECE DETACHEE'

            -- Boîtes vides (Toujours des accessoires)
            WHEN UPPER(title) ~* '(BOITE VIDE|BOÎTE VIDE|BOITIER VIDE|BOÎTIER VIDE|BOÎTE)'
                THEN 'ACCESSOIRE'

            -- Forçage SMARTPHONE : Vrais téléphones ou packs complets (Même si l'annonce liste des accessoires fournis)
            WHEN (UPPER(title) ~* '(IPHONE|GALAXY|SMARTPHONE)' OR UPPER(title) ~* 'SAMSUNG\s*([SAZ]|A\s*\d+)')
                 AND NOT UPPER(title) ~* '(COQUE\s+SEULE|VITRE\s+SEULE|CHARGEUR\s+SEUL|CABLE\s+SEUL)'
                 AND (price > 25 OR UPPER(title) ~* '(RECONDITIONNÉ|DEBLOQUÉ|DÉBLOQUÉ|16GO|32GO|64GO|128GO|256GO|512GO|GIGA)')
                THEN 'SMARTPHONE'

            -- Forçage CONSOLE : Détection des machines (Modernes et Rétro sous les 40€ sauvées)
            WHEN (UPPER(title) ~* '(PLAYSTATION|PLAY\s+STATION|PS5|PS4|PS3|PS2|PS1|PS\s*ONE|PSONE|XBOX|SWITCH|WII|PSP)' OR UPPER(title) LIKE '%CONSOLE%')
                 AND NOT UPPER(title) ~* '(MANETTE\s+SEULE|COQUE\s+SEULE|HOUSSE\s+SEULE|BATTERIE\s+SEULE|SUPPORT\s+SEUL|CHARGEUR\s+SEUL|JEU\s+SEUL|CÂBLE\s+SEUL|CABLE\s+SEUL|ACCESSOIRE\s+SEUL)'
                 AND (price > 15 OR UPPER(title) LIKE '%CONSOLE%')
                THEN 'CONSOLE'

            -- Jeux et Accessoires Standards
            WHEN UPPER(title) ~* '(MANETTE|COQUE|CHARGEUR|CABLE|CÂBLE|SUPPORT|ECOUTEUR|ÉCOUTEUR|BATTERIE|CASQUE|OREILLETTE|VOLANT|PEDALE|SOURIS|CLAVIER|STYLET|STYLLET|AIRPOD|COLLECTOR|EDITION|ÉDITION|JEU\s+CONSOLE|BLU\s*RAY|JEUX|GAME|JEU SONY|JEU MICROSOFT|JEU NINTENDO|JEU XBOX|JEU PS4|JEU PS5|JEU PS3|JEU PS2|JEU PS1|JEU PSP|GEARS OF WAR |FORZA|FIFA|CALL OF DUTY|MARIO|ZELDA|POKEMON|ANIMAL CROSSING|LEGO|GRAND THEFT AUTO|GTA|RED DEAD REDEMPTION|RDR|ASSASSINS CREED|BATTLEFIELD|HALO|OVERWATCH|DESTINY|FORTNITE|ROCKET LEAGUE|RAINBOW SIX|SIEGE|MINECRAFT|CYBERPUNK|WITCHER|FALLOUT|ELDEN RING|BLOODBORNE|DARK SOULS|RESIDENT EVIL|BIOHAZARD|GRAN TURISMO|GTAV?|SPIDER-MAN|MARVEL|DC\s*COMICS|LEGO|DISNEY)' 
                THEN 'ACCESSOIRE'
            
            ELSE UPPER(category) 
        END AS refined_category,

        -- C. Intention de l'annonce
        CASE 
            WHEN UPPER(title) ~* '(CHERCHE|RECHERCHE|ECHANGE|CONTRE|ACHETE|ACHÈTE|REPARE|REPARATION|RÉPARATION|JE CHERCHE|JE RECHERCHE|JE VEUX|JE VENDS|JE VEND)' 
                THEN 'RECHERCHE/SERVICE'
            ELSE 'VENTE'
        END AS listing_intent
    FROM unified_staging
),

-- ====================================================================
-- 2. EXTRACTION DES FEATURES ET CLASSIFICATION PAR MODÈLE
-- ====================================================================
extracted_features AS (
    SELECT
        timestamp,
        ingested_at,
        source,
        refined_category AS category,
        refined_brand AS brand,
        listing_intent,
        title,
        price,
        product_condition,
        url,
        
        CASE 
            -------------------------------------------------------------------
            -- UNIVERS ACCESSOIRES ET PÉRIPHÉRIQUES
            -------------------------------------------------------------------
            WHEN refined_category = 'ACCESSOIRE' AND UPPER(title) ~* '(PS5|PLAYSTATION\s*5|PLAY\s+STATION\s*5)' THEN 'Accessoire PS5'
            WHEN refined_category = 'ACCESSOIRE' AND UPPER(title) ~* '(PS4|PLAYSTATION\s*4|PLAY\s+STATION\s*4)' THEN 'Accessoire PS4'
            WHEN refined_category = 'ACCESSOIRE' AND (UPPER(title) ~* '(XBOX|FORZA|THRUSTMASTER)' OR refined_brand IN ('MICROSOFT', 'THRUSTMASTER')) THEN 'Accessoire Xbox / PC'
            WHEN refined_category = 'ACCESSOIRE' AND UPPER(title) ~* '(IPHONE|APPLE)' THEN 'Accessoire iPhone'
            WHEN refined_category = 'ACCESSOIRE' AND UPPER(title) ~* '(SAMSUNG|GALAXY)' THEN 'Accessoire Samsung'
            WHEN refined_category = 'ACCESSOIRE' AND UPPER(title) ~* '(WII|NINTENDO|SWITCH)' THEN 'Accessoire Nintendo'
            WHEN refined_category = 'ACCESSOIRE' AND (UPPER(title) ~* '(SOURIS|CLAVIER|LOGITECH)' OR refined_brand = 'LOGITECH') THEN 'Accessoire PC / Laptop'
            WHEN refined_category = 'ACCESSOIRE' AND UPPER(title) ~* '(CASQUE|OREILLETTE|ÉCOUTEUR|ECOUTEUR)' THEN 'Casque / Écouteur'
            WHEN refined_category = 'ACCESSOIRE' AND UPPER(title) ~* '(CHARGEUR|CÂBLE|CABLE)' THEN 'Chargeur / Câble'
            WHEN refined_category = 'ACCESSOIRE' AND UPPER(title) ~* '(SOURIS|CLAVIER)' THEN 'Périphérique PC'
            WHEN refined_category = 'PIECE DETACHEE' THEN 'Pièce / Composant Brute'
-------------------------------------------------------------------
            -- UNIVERS APPLE IPHONE (Vrais Téléphones)
            -------------------------------------------------------------------
            WHEN refined_category = 'SMARTPHONE' AND UPPER(title) LIKE '%IPHONE 17 PRO MAX%' THEN 'iPhone 17 Pro Max'
            WHEN refined_category = 'SMARTPHONE' AND UPPER(title) LIKE '%IPHONE 17 PRO%'     THEN 'iPhone 17 Pro'
            WHEN refined_category = 'SMARTPHONE' AND UPPER(title) LIKE '%IPHONE 17 PLUS%'    THEN 'iPhone 17 Plus'
            WHEN refined_category = 'SMARTPHONE' AND UPPER(title) LIKE '%IPHONE 17E%'         THEN 'iPhone 17e'
            WHEN refined_category = 'SMARTPHONE' AND UPPER(title) LIKE '%IPHONE 17%'         THEN 'iPhone 17'
            
            WHEN refined_category = 'SMARTPHONE' AND UPPER(title) LIKE '%IPHONE 16 PRO MAX%' THEN 'iPhone 16 Pro Max'
            WHEN refined_category = 'SMARTPHONE' AND UPPER(title) LIKE '%IPHONE 16 PRO%'     THEN 'iPhone 16 Pro'
            WHEN refined_category = 'SMARTPHONE' AND UPPER(title) LIKE '%IPHONE 16 PLUS%'    THEN 'iPhone 16 Plus'
            WHEN refined_category = 'SMARTPHONE' AND UPPER(title) LIKE '%IPHONE 16%'         THEN 'iPhone 16'
            
            WHEN refined_category = 'SMARTPHONE' AND UPPER(title) LIKE '%IPHONE 15 PRO MAX%' THEN 'iPhone 15 Pro Max'
            WHEN refined_category = 'SMARTPHONE' AND UPPER(title) LIKE '%IPHONE 15 PRO%'     THEN 'iPhone 15 Pro'
            WHEN refined_category = 'SMARTPHONE' AND UPPER(title) LIKE '%IPHONE 15 PLUS%'    THEN 'iPhone 15 Plus'
            WHEN refined_category = 'SMARTPHONE' AND UPPER(title) LIKE '%IPHONE 15%'         THEN 'iPhone 15'
            
            WHEN refined_category = 'SMARTPHONE' AND UPPER(title) LIKE '%IPHONE 14 PRO MAX%' THEN 'iPhone 14 Pro Max'
            WHEN refined_category = 'SMARTPHONE' AND UPPER(title) LIKE '%IPHONE 14 PRO%'     THEN 'iPhone 14 Pro'
            WHEN refined_category = 'SMARTPHONE' AND UPPER(title) LIKE '%IPHONE 14 PLUS%'    THEN 'iPhone 14 Plus'
            WHEN refined_category = 'SMARTPHONE' AND UPPER(title) LIKE '%IPHONE 14%'         THEN 'iPhone 14'
            
            WHEN refined_category = 'SMARTPHONE' AND UPPER(title) LIKE '%IPHONE 13 PRO MAX%' THEN 'iPhone 13 Pro Max'
            WHEN refined_category = 'SMARTPHONE' AND UPPER(title) LIKE '%IPHONE 13 PRO%'     THEN 'iPhone 13 Pro'
            WHEN refined_category = 'SMARTPHONE' AND UPPER(title) LIKE '%IPHONE 13 MINI%'    THEN 'iPhone 13 Mini'
            WHEN refined_category = 'SMARTPHONE' AND UPPER(title) LIKE '%IPHONE 13%'         THEN 'iPhone 13'
            
            WHEN refined_category = 'SMARTPHONE' AND UPPER(title) LIKE '%IPHONE 12 PRO MAX%' THEN 'iPhone 12 Pro Max'
            WHEN refined_category = 'SMARTPHONE' AND UPPER(title) LIKE '%IPHONE 12 PRO%'     THEN 'iPhone 12 Pro'
            WHEN refined_category = 'SMARTPHONE' AND UPPER(title) LIKE '%IPHONE 12 MINI%'    THEN 'iPhone 12 Mini'
            WHEN refined_category = 'SMARTPHONE' AND UPPER(title) LIKE '%IPHONE 12%'         THEN 'iPhone 12'
            
            WHEN refined_category = 'SMARTPHONE' AND UPPER(title) LIKE '%IPHONE 11 PRO MAX%' THEN 'iPhone 11 Pro Max'
            WHEN refined_category = 'SMARTPHONE' AND UPPER(title) LIKE '%IPHONE 11 PRO%'     THEN 'iPhone 11 Pro'
            WHEN refined_category = 'SMARTPHONE' AND UPPER(title) LIKE '%IPHONE 11%'         THEN 'iPhone 11'
            
            WHEN refined_category = 'SMARTPHONE' AND UPPER(title) LIKE '%IPHONE SE%'         THEN 'iPhone SE'
            WHEN refined_category = 'SMARTPHONE' AND UPPER(title) LIKE '%IPHONE X%'          THEN 'iPhone X'
            WHEN refined_category = 'SMARTPHONE' AND UPPER(title) LIKE '%IPHONE XR%'         THEN 'iPhone XR'
            WHEN refined_category = 'SMARTPHONE' AND UPPER(title) LIKE '%IPHONE XS%'         THEN 'iPhone XS'

            -------------------------------------------------------------------
            -- CATALOGUE RESTAURÉ SAMSUNG (Vrais Téléphones)
            -------------------------------------------------------------------
            WHEN refined_category = 'SMARTPHONE' AND UPPER(title) LIKE '%GALAXY S24 ULTRA%' THEN 'Galaxy S24 Ultra'
            WHEN refined_category = 'SMARTPHONE' AND UPPER(title) LIKE '%GALAXY S24+%'       THEN 'Galaxy S24 Plus'
            WHEN refined_category = 'SMARTPHONE' AND UPPER(title) LIKE '%GALAXY S24%'        THEN 'Galaxy S24'
            WHEN refined_category = 'SMARTPHONE' AND UPPER(title) LIKE '%GALAXY S23 ULTRA%' THEN 'Galaxy S23 Ultra'
            WHEN refined_category = 'SMARTPHONE' AND UPPER(title) LIKE '%GALAXY S23+%'       THEN 'Galaxy S23 Plus'
            WHEN refined_category = 'SMARTPHONE' AND UPPER(title) LIKE '%GALAXY S23 FE%'     THEN 'Galaxy S23 FE'
            WHEN refined_category = 'SMARTPHONE' AND UPPER(title) LIKE '%GALAXY S23%'        THEN 'Galaxy S23'
            WHEN refined_category = 'SMARTPHONE' AND UPPER(title) LIKE '%GALAXY S22 ULTRA%' THEN 'Galaxy S22 Ultra'
            WHEN refined_category = 'SMARTPHONE' AND UPPER(title) LIKE '%GALAXY S22+%'       THEN 'Galaxy S22 Plus'
            WHEN refined_category = 'SMARTPHONE' AND UPPER(title) LIKE '%GALAXY S22%'        THEN 'Galaxy S22'
            WHEN refined_category = 'SMARTPHONE' AND UPPER(title) LIKE '%GALAXY S21 ULTRA%' THEN 'Galaxy S21 Ultra'
            WHEN refined_category = 'SMARTPHONE' AND UPPER(title) LIKE '%GALAXY S21+%'       THEN 'Galaxy S21 Plus'
            WHEN refined_category = 'SMARTPHONE' AND UPPER(title) LIKE '%GALAXY S21%'        THEN 'Galaxy S21'
            WHEN refined_category = 'SMARTPHONE' AND UPPER(title) LIKE '%GALAXY NOTE 20 ULTRA%' THEN 'Galaxy Note 20 Ultra'
            WHEN refined_category = 'SMARTPHONE' AND UPPER(title) LIKE '%GALAXY NOTE 20%'       THEN 'Galaxy Note 20'
            
            
            -- Gamme Z (Pliables)
            WHEN refined_category = 'SMARTPHONE' AND UPPER(title) LIKE '%GALAXY Z FOLD 6%'   THEN 'Galaxy Z Fold 6'
            WHEN refined_category = 'SMARTPHONE' AND UPPER(title) LIKE '%GALAXY Z FLIP 6%'   THEN 'Galaxy Z Flip 6'
            WHEN refined_category = 'SMARTPHONE' AND UPPER(title) LIKE '%GALAXY Z FOLD 5%'   THEN 'Galaxy Z Fold 5'
            WHEN refined_category = 'SMARTPHONE' AND UPPER(title) LIKE '%GALAXY Z FLIP 5%'   THEN 'Galaxy Z Flip 5'
            WHEN refined_category = 'SMARTPHONE' AND UPPER(title) LIKE '%GALAXY Z FOLD%'     THEN 'Galaxy Z Fold'
            WHEN refined_category = 'SMARTPHONE' AND UPPER(title) LIKE '%GALAXY Z FLIP%'     THEN 'Galaxy Z Flip'
            WHEN refined_category = 'SMARTPHONE' AND UPPER(title) LIKE '%GALAXY FOLD%'       THEN 'Galaxy Z Fold'
            WHEN refined_category = 'SMARTPHONE' AND UPPER(title) LIKE '%GALAXY FLIP%'       THEN 'Galaxy Z Flip'
            
            -- Gamme A & FE & Historique
            WHEN refined_category = 'SMARTPHONE' AND UPPER(title) LIKE '%GALAXY A55%'        THEN 'Galaxy A55'
            WHEN refined_category = 'SMARTPHONE' AND UPPER(title) LIKE '%GALAXY A35%'        THEN 'Galaxy A35'
            WHEN refined_category = 'SMARTPHONE' AND UPPER(title) LIKE '%GALAXY A15%'        THEN 'Galaxy A15'
            WHEN refined_category = 'SMARTPHONE' AND UPPER(title) LIKE '%GALAXY A54%'        THEN 'Galaxy A54'
            WHEN refined_category = 'SMARTPHONE' AND UPPER(title) LIKE '%GALAXY A34%'        THEN 'Galaxy A34'
            WHEN refined_category = 'SMARTPHONE' AND UPPER(title) LIKE '%GALAXY A14%'        THEN 'Galaxy A14'
            WHEN refined_category = 'SMARTPHONE' AND UPPER(title) LIKE '%GALAXY A53%'        THEN 'Galaxy A53'
            WHEN refined_category = 'SMARTPHONE' AND UPPER(title) ~* '(GALAXY A23|SAMSUNG A 23)' THEN 'Galaxy A23'
            WHEN refined_category = 'SMARTPHONE' AND UPPER(title) LIKE '%GALAXY S4%'         THEN 'Galaxy S4'
            WHEN refined_category = 'SMARTPHONE' AND UPPER(title) LIKE '%GALAXY S5%'         THEN 'Galaxy S5'
            WHEN refined_category = 'SMARTPHONE' AND UPPER(title) LIKE '%GALAXY S6%'         THEN 'Galaxy S6'
            WHEN refined_category = 'SMARTPHONE' AND UPPER(title) LIKE '%GALAXY S7%'         THEN 'Galaxy S7'
            WHEN refined_category = 'SMARTPHONE' AND UPPER(title) LIKE '%GALAXY S8%'         THEN 'Galaxy S8'
            WHEN refined_category = 'SMARTPHONE' AND UPPER(title) LIKE '%GALAXY S9%'         THEN 'Galaxy S9'
            WHEN refined_category = 'SMARTPHONE' AND UPPER(title) LIKE '%GALAXY S10%'        THEN 'Galaxy S10'
            WHEN refined_category = 'SMARTPHONE' AND UPPER(title) LIKE '%GALAXY S20%'        THEN 'Galaxy S20'
            WHEN refined_category = 'SMARTPHONE' AND UPPER(title) LIKE '%GALAXY S21%'        THEN 'Galaxy S21'
            WHEN refined_category = 'SMARTPHONE' AND UPPER(title) LIKE '%GALAXY S22%'        THEN 'Galaxy S22'
            WHEN refined_category = 'SMARTPHONE' AND UPPER(title) LIKE '%GALAXY S23%'        THEN 'Galaxy S23'
            WHEN refined_category = 'SMARTPHONE' AND UPPER(title) LIKE '%GALAXY NOTE 10%'    THEN 'Galaxy Note 10'
            WHEN refined_category = 'SMARTPHONE' AND UPPER(title) LIKE '%GALAXY NOTE 9%'     THEN 'Galaxy Note 9'
            WHEN refined_category = 'SMARTPHONE' AND UPPER(title) LIKE '%GALAXY NOTE 8%'     THEN 'Galaxy Note 8'
            WHEN refined_category = 'SMARTPHONE' AND UPPER(title) LIKE '%GALAXY NOTE 7%'     THEN 'Galaxy Note 7'
            
            

            -------------------------------------------------------------------
            -- UNIVERS CONSOLES RESTAURÉ (Vraies Machines)
            -------------------------------------------------------------------
            WHEN refined_category = 'CONSOLE' AND (UPPER(title) LIKE '%PLAYSTATION 5 PRO%' OR UPPER(title) LIKE '%PS5 PRO%') THEN 'PlayStation 5 Pro'
            WHEN refined_category = 'CONSOLE' AND (UPPER(title) LIKE '%PLAYSTATION 5 SLIM%' OR UPPER(title) LIKE '%PS5 SLIM%') THEN 'PlayStation 5 Slim'
            WHEN refined_category = 'CONSOLE' AND (UPPER(title) LIKE '%PLAYSTATION 5%' OR UPPER(title) LIKE '%PS5%') THEN 'PlayStation 5'
            WHEN refined_category = 'CONSOLE' AND (UPPER(title) LIKE '%PLAYSTATION 4 PRO%' OR UPPER(title) LIKE '%PS4 PRO%') THEN 'PlayStation 4 Pro'
            WHEN refined_category = 'CONSOLE' AND (UPPER(title) LIKE '%PLAYSTATION 4 SLIM%' OR UPPER(title) LIKE '%PS4 SLIM%') THEN 'PlayStation 4 Slim'
            WHEN refined_category = 'CONSOLE' AND (UPPER(title) LIKE '%PLAYSTATION 4%' OR UPPER(title) LIKE '%PS4%') THEN 'PlayStation 4'
            WHEN refined_category = 'CONSOLE' AND (UPPER(title) LIKE '%PLAYSTATION 3%' OR UPPER(title) LIKE '%PS3%') THEN 'PlayStation 3'
            WHEN refined_category = 'CONSOLE' AND (UPPER(title) LIKE '%PLAYSTATION 2%' OR UPPER(title) LIKE '%PS2%') THEN 'PlayStation 2'
            WHEN refined_category = 'CONSOLE' AND (UPPER(title) ~* '(PLAYSTATION\s*1|PS1|PS\s*ONE|PSONE)') THEN 'PlayStation 1'
            WHEN refined_category = 'CONSOLE' AND UPPER(title) LIKE '%PSP%'                  THEN 'PlayStation Portable (PSP)'
            WHEN refined_category = 'CONSOLE' AND UPPER(title) LIKE '%XBOX SERIES X%'       THEN 'Xbox Series X'
            WHEN refined_category = 'CONSOLE' AND UPPER(title) LIKE '%XBOX SERIES S%'       THEN 'Xbox Series S'
            WHEN refined_category = 'CONSOLE' AND UPPER(title) LIKE '%XBOX ONE X%'          THEN 'Xbox One X'
            WHEN refined_category = 'CONSOLE' AND UPPER(title) LIKE '%XBOX ONE S%'          THEN 'Xbox One S'
            WHEN refined_category = 'CONSOLE' AND UPPER(title) LIKE '%XBOX ONE%'             THEN 'Xbox One'
            WHEN refined_category = 'CONSOLE' AND UPPER(title) LIKE '%NINTENDO SWITCH PRO%' THEN 'Nintendo Switch Pro'
            WHEN refined_category = 'CONSOLE' AND UPPER(title) LIKE '%NINTENDO SWITCH OLED%' THEN 'Nintendo Switch OLED'
            WHEN refined_category = 'CONSOLE' AND UPPER(title) LIKE '%NINTENDO SWITCH LITE%' THEN 'Nintendo Switch LITE'
            WHEN refined_category = 'CONSOLE' AND UPPER(title) LIKE '%NINTENDO SWITCH%'      THEN 'Nintendo Switch'
            WHEN refined_category = 'CONSOLE' AND UPPER(title) LIKE '%WII%'                  THEN 'Nintendo Wii'
            WHEN refined_category = 'CONSOLE' AND UPPER(title) LIKE '%PLAYSTATION VITA%'     THEN 'PlayStation Vita'
            WHEN refined_category = 'CONSOLE' AND UPPER(title) LIKE '%PLAYSTATION PORTAL%'       THEN 'PlayStation PORTAL'

            -------------------------------------------------------------------
            -- CATALOGUE RESTAURÉ ET CORRIGÉ LAPTOPS / ORDINATEURS
            -------------------------------------------------------------------
            -- Apple Laptops
            WHEN refined_category = 'ORDINATEUR' AND UPPER(title) LIKE '%MACBOOK PRO M4%' THEN 'MacBook Pro M4'
            WHEN refined_category = 'ORDINATEUR' AND UPPER(title) LIKE '%MACBOOK PRO M3%' THEN 'MacBook Pro M3'
            WHEN refined_category = 'ORDINATEUR' AND UPPER(title) LIKE '%MACBOOK PRO M2%' THEN 'MacBook Pro M2'
            WHEN refined_category = 'ORDINATEUR' AND UPPER(title) LIKE '%MACBOOK PRO M1%' THEN 'MacBook Pro M1'
            
            -- MacBook Pro Touch Bar 
            WHEN refined_category = 'ORDINATEUR' AND UPPER(title) LIKE '%MACBOOK PRO TOUCH BAR 13%' THEN 'MacBook Pro Touch Bar 13 Pouces'
            WHEN refined_category = 'ORDINATEUR' AND UPPER(title) LIKE '%MACBOOK PRO TOUCH BAR 14%' THEN 'MacBook Pro Touch Bar 14 Pouces'
            WHEN refined_category = 'ORDINATEUR' AND UPPER(title) LIKE '%MACBOOK PRO TOUCH BAR 15%' THEN 'MacBook Pro Touch Bar 15 Pouces'
            WHEN refined_category = 'ORDINATEUR' AND UPPER(title) LIKE '%MACBOOK PRO TOUCH BAR 16%' THEN 'MacBook Pro Touch Bar 16 Pouces'
            WHEN refined_category = 'ORDINATEUR' AND UPPER(title) LIKE '%MACBOOK PRO TOUCH BAR 17%' THEN 'MacBook Pro Touch Bar 17 Pouces'

            -- MacBook Pro & Air Standards
            WHEN refined_category = 'ORDINATEUR' AND UPPER(title) LIKE '%MACBOOK PRO 13%'       THEN 'MacBook Pro 13 Pouces'
            WHEN refined_category = 'ORDINATEUR' AND UPPER(title) LIKE '%MACBOOK PRO 14%'       THEN 'MacBook Pro 14 Pouces'
            WHEN refined_category = 'ORDINATEUR' AND UPPER(title) LIKE '%MACBOOK PRO 16%'       THEN 'MacBook Pro 16 Pouces'
            WHEN refined_category = 'ORDINATEUR' AND UPPER(title) LIKE '%MACBOOK AIR M3%'       THEN 'MacBook Air M3'
            WHEN refined_category = 'ORDINATEUR' AND UPPER(title) LIKE '%MACBOOK AIR M2%'       THEN 'MacBook Air M2'
            WHEN refined_category = 'ORDINATEUR' AND UPPER(title) LIKE '%MACBOOK AIR M1%'       THEN 'MacBook Air M1'
            WHEN refined_category = 'ORDINATEUR' AND UPPER(title) LIKE '%MACBOOK AIR 13%'       THEN 'MacBook Air 13 Pouces'
            WHEN refined_category = 'ORDINATEUR' AND UPPER(title) LIKE '%MACBOOK AIR 15%'       THEN 'MacBook Air 15 Pouces'
            
            -- PC Laptops Premium & Business
            WHEN refined_category = 'ORDINATEUR' AND UPPER(title) LIKE '%DELL XPS%'       THEN 'Dell XPS'
            WHEN refined_category = 'ORDINATEUR' AND UPPER(title) LIKE '%THINKPAD%'       THEN 'Lenovo ThinkPad'
            WHEN refined_category = 'ORDINATEUR' AND UPPER(title) LIKE '%ZENBOOK%'        THEN 'Asus ZenBook'
            WHEN refined_category = 'ORDINATEUR' AND UPPER(title) LIKE '%VIVOBOOK%'       THEN 'Asus VivoBook'
            WHEN refined_category = 'ORDINATEUR' AND UPPER(title) LIKE '%INSPIRON%'       THEN 'Dell Inspiron'
            WHEN refined_category = 'ORDINATEUR' AND UPPER(title) LIKE '%ENVY%'          THEN 'HP Envy'
            WHEN refined_category = 'ORDINATEUR' AND UPPER(title) LIKE '%SPECTRE%'       THEN 'HP Spectre'
            WHEN refined_category = 'ORDINATEUR' AND UPPER(title) LIKE '%LATITUDE%'       THEN 'Dell Latitude'
            WHEN refined_category = 'ORDINATEUR' AND UPPER(title) LIKE '%LATITUDE%'       THEN 'Dell Latitude'
            WHEN refined_category = 'ORDINATEUR' AND UPPER(title) LIKE '%SURFACE%'       THEN 'Microsoft Surface'

            
            -- Laptops Gaming & Grand Public
            WHEN refined_category = 'ORDINATEUR' AND UPPER(title) LIKE '%SURFACE LAPTOP%' THEN 'Microsoft Surface'
            WHEN refined_category = 'ORDINATEUR' AND UPPER(title) LIKE '%SURFACE PRO%'    THEN 'Microsoft Surface Pro'
            WHEN refined_category = 'ORDINATEUR' AND UPPER(title) LIKE '%ROG ZEPHYRUS%'   THEN 'Asus ROG Zephyrus'
            WHEN refined_category = 'ORDINATEUR' AND UPPER(title) LIKE '%ROG STRIX%'      THEN 'Asus ROG Strix'
            WHEN refined_category = 'ORDINATEUR' AND UPPER(title) LIKE '%ALIENWARE%'      THEN 'Dell Alienware'
            WHEN refined_category = 'ORDINATEUR' AND UPPER(title) LIKE '%HP SPECTRE%'     THEN 'HP Spectre'
            WHEN refined_category = 'ORDINATEUR' AND UPPER(title) LIKE '%HP ENVY%'        THEN 'HP Envy'
            WHEN refined_category = 'ORDINATEUR' AND UPPER(title) LIKE '%HP PAVILION%'    THEN 'HP Pavilion'
            WHEN refined_category = 'ORDINATEUR' AND UPPER(title) LIKE '%LENOVO YOGA%'    THEN 'Lenovo Yoga'
            WHEN refined_category = 'ORDINATEUR' AND UPPER(title) LIKE '%LEGION%'         THEN 'Lenovo Legion'
            WHEN refined_category = 'ORDINATEUR' AND UPPER(title) LIKE '%ACER NITRO%'     THEN 'Acer Nitro'
            WHEN refined_category = 'ORDINATEUR' AND UPPER(title) LIKE '%ACER PREDATOR%'  THEN 'Acer Predator'
            WHEN refined_category = 'ORDINATEUR' AND UPPER(title) LIKE '%ACER SWIFT%'     THEN 'Acer Swift'            
            WHEN refined_category = 'ORDINATEUR' AND UPPER(title) LIKE '%ASUS TUF%'       THEN 'Asus TUF'
            WHEN refined_category = 'ORDINATEUR' AND UPPER(title) LIKE '%ASUS VIVOBOOK%'   THEN 'Asus VivoBook'
            WHEN refined_category = 'ORDINATEUR' AND UPPER(title) LIKE '%ASUS ZENBOOK%'     THEN 'Asus ZenBook'
            -- ajoute des models supplémentaires ici selon les besoins (acer swift, hp pavilion, amd, ryzen, etc.)
            WHEN refined_category = 'ORDINATEUR' AND UPPER(title) LIKE '%ACER SWIFT%'     THEN 'Acer Swift'
            WHEN refined_category = 'ORDINATEUR' AND UPPER(title) LIKE '%HP PAVILION%'    THEN 'HP Pavilion'
            WHEN refined_category = 'ORDINATEUR' AND UPPER(title) LIKE '%LENOVO LEGION%'    THEN 'Lenovo Legion'
            WHEN refined_category = 'ORDINATEUR' AND UPPER(title) LIKE '%ACER PREDATOR%'    THEN 'Acer Predator'    
            

            ---
            -- 1. HANDHELDS (PC Consoles portables)
            WHEN refined_category = 'ORDINATEUR' AND UPPER(title) LIKE '%ROG ALLY X%' THEN 'Asus ROG Ally X'
            WHEN refined_category = 'ORDINATEUR' AND UPPER(title) LIKE '%ROG ALLY%'  THEN 'Asus ROG Ally'
            WHEN refined_category = 'ORDINATEUR' AND UPPER(title) LIKE '%MSI CLAW%'  THEN 'MSI Claw'

            -- 2. HP
            WHEN refined_category = 'ORDINATEUR' AND UPPER(title) LIKE '%ELITEBOOK%' THEN 'HP EliteBook'
            WHEN refined_category = 'ORDINATEUR' AND UPPER(title) LIKE '%PROBOOK%'  THEN 'HP ProBook'
            WHEN refined_category = 'ORDINATEUR' AND UPPER(title) LIKE '%ZBOOK%'    THEN 'HP ZBook'
            WHEN refined_category = 'ORDINATEUR' AND UPPER(title) LIKE '%SPECTRE%'  THEN 'HP Spectre'
            WHEN refined_category = 'ORDINATEUR' AND UPPER(title) LIKE '%ENVY%'     THEN 'HP Envy'
            WHEN refined_category = 'ORDINATEUR' AND UPPER(title) LIKE '%OMEN%'     THEN 'HP Omen'
            WHEN refined_category = 'ORDINATEUR' AND UPPER(title) LIKE '%PAVILION%' THEN 'HP Pavilion'

            -- 3. ASUS
            WHEN refined_category = 'ORDINATEUR' AND UPPER(title) LIKE '%ZENBOOK%'    THEN 'Asus ZenBook'
            WHEN refined_category = 'ORDINATEUR' AND UPPER(title) LIKE '%VIVOBOOK%'   THEN 'Asus VivoBook'
            WHEN refined_category = 'ORDINATEUR' AND UPPER(title) LIKE '%ROG ZEPHYRUS%' THEN 'Asus ROG Zephyrus'
            WHEN refined_category = 'ORDINATEUR' AND UPPER(title) LIKE '%ROG STRIX%'  THEN 'Asus ROG Strix'
            WHEN refined_category = 'ORDINATEUR' AND UPPER(title) LIKE '%TUF%'        THEN 'Asus TUF'
            WHEN refined_category = 'ORDINATEUR' AND UPPER(title) LIKE '%EXPERTBOOK%' THEN 'Asus ExpertBook'

            -- 4. LENOVO
            WHEN refined_category = 'ORDINATEUR' AND UPPER(title) LIKE '%THINKPAD%' THEN 'Lenovo ThinkPad'
            WHEN refined_category = 'ORDINATEUR' AND UPPER(title) LIKE '%IDEAPAD%'  THEN 'Lenovo IdeaPad'
            WHEN refined_category = 'ORDINATEUR' AND UPPER(title) LIKE '%YOGA%'     THEN 'Lenovo Yoga'
            WHEN refined_category = 'ORDINATEUR' AND UPPER(title) LIKE '%LEGION%'   THEN 'Lenovo Legion'

            -- 5. DELL
            WHEN refined_category = 'ORDINATEUR' AND UPPER(title) LIKE '%ALIENWARE%' THEN 'Dell Alienware'
            WHEN refined_category = 'ORDINATEUR' AND UPPER(title) LIKE '%PRECISION%' THEN 'Dell Precision'
            WHEN refined_category = 'ORDINATEUR' AND UPPER(title) LIKE '%LATITUDE%'  THEN 'Dell Latitude'
            WHEN refined_category = 'ORDINATEUR' AND UPPER(title) LIKE '%INSPIRON%'  THEN 'Dell Inspiron'
            WHEN refined_category = 'ORDINATEUR' AND UPPER(title) LIKE '%XPS%'       THEN 'Dell XPS'

            -- 6. MSI
            WHEN refined_category = 'ORDINATEUR' AND UPPER(title) LIKE '%KATANA%'     THEN 'MSI Katana'
            WHEN refined_category = 'ORDINATEUR' AND UPPER(title) LIKE '%CYBORG%'     THEN 'MSI Cyborg'
            WHEN refined_category = 'ORDINATEUR' AND UPPER(title) LIKE '%CROSSHAIR%'  THEN 'MSI Crosshair'
            WHEN refined_category = 'ORDINATEUR' AND UPPER(title) LIKE '%PULSE%'      THEN 'MSI Pulse'
            WHEN refined_category = 'ORDINATEUR' AND (UPPER(title) LIKE '%THIN GF63%' OR UPPER(title) LIKE '%GF63%') THEN 'MSI Thin'

            -- 7. AUTRES & CHROMEBOOKS
            WHEN refined_category = 'ORDINATEUR' AND UPPER(title) LIKE '%SURFACE LAPTOP%' THEN 'Microsoft Surface'
            WHEN refined_category = 'ORDINATEUR' AND UPPER(title) LIKE '%SURFACE PRO%'    THEN 'Microsoft Surface Pro'
            WHEN refined_category = 'ORDINATEUR' AND UPPER(title) LIKE '%PREDATOR%'       THEN 'Acer Predator'
            WHEN refined_category = 'ORDINATEUR' AND UPPER(title) LIKE '%NITRO%'          THEN 'Acer Nitro'
            WHEN refined_category = 'ORDINATEUR' AND UPPER(title) LIKE '%SWIFT%'          THEN 'Acer Swift'
            WHEN refined_category = 'ORDINATEUR' AND UPPER(title) LIKE '%CHROMEBOOK%'     THEN 'Chromebook'
            ELSE 'Modèle non répertorié'
        END AS product_model,

        -- D. EXTRACTION DU STOCKAGE (Ajout du support pour 'GIGA' et '40GO')
        CASE 
            WHEN title ~* '1\s*(to|tb)'              THEN '1 To'
            WHEN title ~* '2\s*(to|tb)'              THEN '2 To'
            WHEN title ~* '512\s*(go|gb|giga)'        THEN '512 Go'
            WHEN title ~* '256\s*(go|gb|giga)'        THEN '256 Go'
            WHEN title ~* '128\s*(go|gb|giga)'        THEN '128 Go'
            WHEN title ~* '64\s*(go|gb|giga)'         THEN '64 Go'
            WHEN title ~* '40\s*(go|gb|giga)'         THEN '40 Go'
            WHEN title ~* '32\s*(go|gb|giga)'         THEN '32 Go'
            WHEN title ~* '16\s*(go|gb|giga)'         THEN '16 Go'
            WHEN title ~* '825\s*(go|gb|giga)'        THEN '825 Go'
            WHEN title ~* '500\s*(go|gb|giga)'        THEN '500 Go'
            ELSE 'Non spécifié'
        END AS storage_capacity,

        -- E. EXTRACTION TAILLE D'ÉCRAN
        CASE 
            WHEN title ~* '13(\.,[0-9])?''?' OR title ~* '13-inch' OR title ~* '13\.3' THEN '13 pouces'
            WHEN title ~* '14(\.,[0-9])?''?' OR title ~* '14-inch'                    THEN '14 pouces'
            WHEN title ~* '15(\.,[0-9])?''?' OR title ~* '15-inch' OR title ~* '15\.6' THEN '15 pouces'
            WHEN title ~* '16(\.,[0-9])?''?' OR title ~* '16-inch'                    THEN '16 pouces'
            WHEN title ~* '17(\.,[0-9])?''?' OR title ~* '17-inch' OR title ~* '17\.3' THEN '17 pouces'
            ELSE NULL
        END AS screen_size


    FROM refined_base
)

-- ====================================================================
-- 3. SÉLECTION FINALE ET CLÉ UNIQUE MD5
-- ====================================================================
SELECT
    md5(concat(source, title, price::text, timestamp::text)) AS product_id,
    timestamp,
    ingested_at,
    source,
    category,
    brand,
    listing_intent,
    product_model,
    storage_capacity,
    screen_size,
    title,
    price,
    product_condition,
    url
FROM extracted_features