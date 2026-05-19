# 🏗️ Architecture Détaillée - Diagrammes & Explications

## Vue d'ensemble: 6 Étages du Pipeline

```
┌─────────────────────────────────────────────────────────────────┐
│                  ÉTAGE 6: VISUALISATION                         │
│         📊 Streamlit Dashboard (Port 8501)                      │
│  - Graphiques interactifs                                       │
│  - Filtres avancés (catégorie, prix, vendeur)                  │
│  - Alertes deals en live                                        │
└──────────────────────────┬──────────────────────────────────────┘
                           ▲
                           │ SELECT * FROM final_data
                           │
┌──────────────────────────┴──────────────────────────────────────┐
│            ÉTAGE 5: DATA WAREHOUSE & ANALYTICS                 │
│      🗄️ PostgreSQL - Table "final_data" (40+ colonnes)         │
│  ┌────────────────────────────────────────────────────────┐   │
│  │ Exemple Row:                                           │   │
│  │ - timestamp, source, title, price                      │   │
│  │ - category, type, sub_category                         │   │
│  │ - market_volume, median_price, avg_price               │   │
│  │ - z_score, pct_deviation                               │   │
│  │ - deal_score (💎/🔥/❌/📊)                              │   │
│  │ - operational_status (🚨/💤/🟢)                         │   │
│  │ - estimated_resell_profit                              │   │
│  └────────────────────────────────────────────────────────┘   │
└──────────────────────────┬──────────────────────────────────────┘
                           ▲
                           │ dbt run --models shopping (3-5 sec)
                           │
┌──────────────────────────┴──────────────────────────────────────┐
│     ÉTAGE 4: TRANSFORMATION (dbt - Data Build Tool)            │
│  ┌────────────────────────────────────────────────────────┐   │
│  │ Staging Layer:                                         │   │
│  │ - stg_ebay.sql          (Normalise, Parse prix)      │   │
│  │ - stg_leboncoin.sql     (Gère 1.299,99€ français)    │   │
│  │ - stg_cashexpress.sql   (État: Neuf/Occasion)        │   │
│  │ - stg_amazon.sql        (Unifie schéma)              │   │
│  └────────────────────────────────────────────────────────┘   │
│  ┌────────────────────────────────────────────────────────┐   │
│  │ Intermediate Layer:                                    │   │
│  │ - int_classified_products.sql                          │   │
│  │   • LAYER 1: 100+ hardcoded patterns (brands)         │   │
│  │   • LAYER 1-SPÉ: Jeux, Magazines, Accessoires       │   │
│  │   • LAYER 2: 240+ CSV rules + priorité              │   │
│  │   • LAYERS 3-6: Fallback chain                        │   │
│  │   → Sortie: category + type intelligents              │   │
│  └────────────────────────────────────────────────────────┘   │
│  ┌────────────────────────────────────────────────────────┐   │
│  │ Marts Layer:                                           │   │
│  │ - final_data.sql                                       │   │
│  │   • Déduplication                                      │   │
│  │   • Calcul statistiques (Z-score, volatilité)         │   │
│  │   • Scoring deals (💎/🔥/❌)                            │   │
│  │   • Tri par rentabilité                               │   │
│  └────────────────────────────────────────────────────────┘   │
└──────────────────────────┬──────────────────────────────────────┘
                           ▲
                           │ PySpark APPEND
                           │
┌──────────────────────────┴──────────────────────────────────────┐
│    ÉTAGE 3: INGESTION (Apache Spark - Data Processing)         │
│  ┌────────────────────────────────────────────────────────┐   │
│  │ Job: load_to_postgres.py                              │   │
│  │ 1. Lit CSV brut depuis /data/processed/               │   │
│  │ 2. Ajoute métadonnées (search_keyword, timestamp)    │   │
│  │ 3. Écrit dans PostgreSQL (mode APPEND)               │   │
│  │ 4. Archive CSV                                        │   │
│  │                                                        │   │
│  │ Architecture Spark:                                   │   │
│  │ ┌─── Spark Master ───────┐                           │   │
│  │ │  Coordinateur du job   │                           │   │
│  │ └──────────┬─────────────┘                           │   │
│  │            │ Distribue le travail                     │   │
│  │       ┌────┴──────┬──────────┐                        │   │
│  │       ▼           ▼          ▼                        │   │
│  │   Worker 1    Worker 2   Worker 3                    │   │
│  │   Partitions Partitions Partitions                   │   │
│  │                                                        │   │
│  │ Résultat: Tables RAW dans PostgreSQL                 │   │
│  │ - raw_ebay (1234+ lignes)                            │   │
│  │ - raw_leboncoin (1955+ lignes)                       │   │
│  │ - raw_cashexpress (500+ lignes)                      │   │
│  │ - raw_amazon (0-100+ lignes)                         │   │
│  └────────────────────────────────────────────────────────┘   │
└──────────────────────────┬──────────────────────────────────────┘
                           ▲
                           │ Lecture CSV
                           │
┌──────────────────────────┴──────────────────────────────────────┐
│  ÉTAGE 2: ORCHESTRATION (Apache Airflow - Workflow Manager)    │
│  ┌────────────────────────────────────────────────────────┐   │
│  │ DAG: smart_buy_sentinel_pipeline                       │   │
│  │ Schedule: 43 5 * * * (Quotidien 7h43 Paris)          │   │
│  │                                                        │   │
│  │    ┌──────────────────────────────────────┐          │   │
│  │    │ INPUT: search_query = "console"     │          │   │
│  │    └──────────────────┬───────────────────┘          │   │
│  │                       │                              │   │
│  │  ┌────────────────────┼────────────────────┐        │   │
│  │  │ Parallélisation:   │                    │        │   │
│  │  ▼                    ▼                    ▼        │   │
│  │  scrape_ebay    scrape_amazon   scrape_cashexpress  │   │
│  │      │                │                   │        │   │
│  │  scrape_leboncoin◄────┴───────────────────┘        │   │
│  │      │                                              │   │
│  │      └──────────────────┬──────────────────────┐   │   │
│  │                         ▼                      │   │   │
│  │                spark_load_to_postgres         │   │   │
│  │                         │                      │   │   │
│  │                         ▼                      │   │   │
│  │        dbt_transformation_shopping             │   │   │
│  │                         │                      │   │   │
│  │                         ▼                      │   │   │
│  │              send_deals_telegram               │   │   │
│  │                    (SUCCESS)                   │   │   │
│  └────────────────────────────────────────────────┘   │   │
│                                                        │   │
│  Accessible: http://localhost:8081                    │   │
│  Admin UI: Voir le DAG, logs, re-run, debug          │   │
└──────────────────────────┬──────────────────────────────────────┘
                           ▲
                           │ Fichiers CSV
                           │
┌──────────────────────────┴──────────────────────────────────────┐
│         ÉTAGE 1: INGESTION BRUTE (Web Scraping)                │
│  ┌────────────────────────────────────────────────────────┐   │
│  │ 4 Scrapers parallélisés (BeautifulSoup4 + Requests)   │   │
│  │                                                        │   │
│  │  ebay_scraper.py          → eBay.com              │   │
│  │       ↓                                               │   │
│  │  20260520_142530_ebay_search_console.csv             │   │
│  │                                                        │   │
│  │  leboncoin_scraper.py     → LeBonCoin.fr            │   │
│  │       ↓                                               │   │
│  │  20260520_142532_lbc_search_console.csv              │   │
│  │                                                        │   │
│  │  amazon_scraper.py        → Amazon.fr               │   │
│  │       ↓                                               │   │
│  │  20260520_142534_amazon_search_console.csv           │   │
│  │                                                        │   │
│  │  cashexpress_scraper.py   → CashExpress.fr          │   │
│  │       ↓                                               │   │
│  │  20260520_142536_cashexpress_search_console.csv      │   │
│  │                                                        │   │
│  │ Format CSV: title | price | etat | url | timestamp  │   │
│  │ Stored in: /data/processed/used-data-shop/          │   │
│  └────────────────────────────────────────────────────────┘   │
│                                                        │   │
│ ⏰ Durée totale: 7-10 minutes (tout le pipeline)       │   │
└────────────────────────────────────────────────────────────────┘
```

---

## Classification Intelligente (6-Couches)

### Exemple 1: "JEU PS5 ANNO 1800"

```
COUCHE 1 (100+ hardcoded brands)
├─ Match "%playstation%" ? → OUI mais pas spécifique
└─ Continue...

COUCHE 1-SPÉCIFIQUES (Jeux, Magazines, etc.)
├─ Match "%anno 1800%" ? → OUI! ✨
└─ Classification FINALE: "💿 Jeu Vidéo" (STOP ici)

N'évalue pas COUCHES 2-6 (déjà trouvé match prioritaire)
```

### Exemple 2: "Télécommande Samsung PS5"

```
COUCHE 1
├─ Match "%samsung%" ? → OUI mais pas assez spécifique
└─ Continue...

COUCHE 1-SPÉCIFIQUES
├─ Match "%telecomande%"? → OUI ✨
└─ Classification FINALE: "🎮 Accessoire Console" (STOP)

Pourquoi pas "%ps5%" de la COUCHE 1?
→ Parce que "%telecomande%" dans COUCHE 1-SPÉ a PRIORITÉ
→ L'ordre d'évaluation dans le CASE statement est CRUCIAL!
```

### Exemple 3: "Coque iPhone 15 Rose"

```
COUCHE 1
├─ Match "%iphone%" ? → OUI mais pas spécifique
└─ Continue...

COUCHE 1-SPÉCIFIQUES
├─ Match jeux/magazines/accessoires ? → NON
└─ Continue...

COUCHE 2 (CSV rules avec priorité)
├─ Cherche dans mapping_sub_categories.csv
├─ Match "%iphone% %coque%" Priority=1 ? → OUI ✨
└─ Classification: "🔌 Accessoire Téléphone" (STOP)
```

---

## Flux de Données PostgreSQL

### Tables RAW (Input)

```
raw_ebay                    raw_leboncoin
┌─────────────────────┐    ┌─────────────────────┐
│ id (serial)         │    │ id (serial)         │
│ title (text)        │    │ title (text)        │
│ price_raw (text)    │    │ price_raw (text)    │
│ etat (text)         │    │ etat (text)         │
│ url (text)          │    │ url (text)          │
│ search_keyword      │    │ search_keyword      │
│ ingested_at (ts)    │    │ ingested_at (ts)    │
└─────────────────────┘    └─────────────────────┘
1234+ rows                 1955+ rows

raw_cashexpress            raw_amazon
┌─────────────────────┐    ┌─────────────────────┐
│ ... (même schéma)   │    │ ... (même schéma)   │
└─────────────────────┘    └─────────────────────┘
500+ rows                  0-100 rows
```

### Tables STAGING (Nettoyées)

```
stg_ebay (VIEW)
┌──────────────────────────────────────┐
│ timestamp (DATE clean)               │
│ source = 'ebay'                      │
│ search_keyword (LOWER TRIM)          │
│ title (TRIM)                         │
│ product_brand (parsed ou NULL)       │
│ price (DOUBLE PRECISION) ✨          │ ← Conversion intelligente
│ etat (normalized)                    │
│ url                                  │
└──────────────────────────────────────┘
Exemple: "20,50€" → "20.50" → 20.50 (numeric)
```

### Table INTERMEDIATE (Classifiée)

```
int_classified_products (VIEW)
┌──────────────────────────────────────┐
│ [Tous les champs stg]                │
├──────────────────────────────────────┤
│ + sub_category (6-couches)   ✨      │
│   Ex: "📱 Smartphone" ou             │
│        "🕹️ Console Nintendo DS"      │
│                                      │
│ + category (parsed)                  │
│   Ex: "📱 Smartphone" ou             │
│        "🕹️ Console"                  │
│                                      │
│ + type (parsed)                      │
│   Ex: "Apple" ou "iPhone 15 Pro"    │
│        "Nintendo DS"                 │
└──────────────────────────────────────┘
```

### Table FINAL_DATA (Analytics)

```
final_data (TABLE - Persistée)
┌──────────────────────────────────────────────────────┐
│ [Champs classification + pricing]                     │
├──────────────────────────────────────────────────────┤
│ STATISTIQUES:                                         │
│ - market_volume (COUNT par category)                  │
│ - median_market_price                                │
│ - avg_market_price                                   │
│ - price_volatility (STDDEV)                          │
├──────────────────────────────────────────────────────┤
│ CALCULS:                                              │
│ - z_score = (price - avg) / stddev                   │
│ - pct_deviation = ((price - median) / median) * 100  │
│ - estimated_resell_profit = median - price           │
├──────────────────────────────────────────────────────┤
│ SCORING:                                              │
│ - deal_score:                                         │
│   💎 ANOMALIE (z < -2 ET profit > 30€)              │
│   🔥 EXCELLENT (z < -1.5 AND profit > 20€)         │
│   ❌ SURÉVALUÉ (price > median * 1.2)               │
│   📊 PRIX MARCHÉ (default)                           │
│                                                       │
│ - operational_status:                                │
│   🚨 SNIPER (< 1h old ET excellent deal)            │
│   💤 OBSOLÈTE (> 48h old)                           │
│   🟢 STABLE (other)                                  │
├──────────────────────────────────────────────────────┤
│ TRI: deal_score DESC, profit DESC, age ASC            │
│      Meilleurs deals en premier!                      │
└──────────────────────────────────────────────────────┘
```

---

## Extraction du Prix - Algorithme

### Problèmes rencontrés

```
Input: "20.50€ neuf"      → Attendu: 20.50
Input: "1.299,99 euros"   → Attendu: 1299.99 (français!)
Input: "20..99€"          → Attendu: 20.99 (format cassé)
Input: "EUR 15"           → Attendu: 15.00
Input: "prix: N/A"        → Attendu: NULL
```

### Solution robuste

```sql
CASE 
    WHEN price_raw ~ '[0-9]+[.,][0-9]{2}' THEN
        -- Format avec 2 décimales détecté
        REPLACE(
            SUBSTRING(price_raw FROM '[0-9]{1,}[.,][0-9]{2}$'),  -- $ = fin de chaîne
            ',', '.'
        )
    WHEN price_raw ~ '[0-9]+' THEN
        -- Juste des chiffres
        SUBSTRING(price_raw FROM '[0-9]+$')
    ELSE 
        -- Pas de prix valide
        NULL
END

Clés:
- [0-9]{1,}        → Cherche le DERNIER nombre (fin de chaîne)
- [.,]             → Accepte virgule OU point comme séparateur
- $                → Ancre FIN (pas les séparateurs au début)
- REPLACE(,, .)   → Convertit virgule française en point SQL
```

---

## Déploiement Physique (Docker Compose)

```
Host Machine (Votre PC)
│
├─ Port 8081  ←─────────────┐
├─ Port 8501  ←─────────────┤
├─ Port 5432  ←─────────────┤
├─ Port 8082  ←─────────────┤
│             │              │
▼             │              │
Docker Daemon │              │
    │         │              │
    ├─────────┼──────────────┼─────────────────────────────┐
    │         │              │                             │
    │    ┌────▼────┐    ┌────▼────┐                    ┌───▼───┐
    │    │ Airflow │    │PostgreSQL│                    │Spark  │
    │    │Container│    │Container │                    │Master │
    │    ├─────────┤    ├──────────┤                    ├───────┤
    │    │Airflow  │    │Base dato │                    │Master │
    │    │WebServer│    │Airflow   │                    │service│
    │    │Scheduler│    │+ Smart   │                    └───────┘
    │    │dbt      │    │Buy data  │          ┌──────────────┐
    │    │Spark CLI│    └──────────┘          │Spark Worker  │
    │    └─────────┘                          ├──────────────┤
    │                                         │Worker service│
    │    ┌──────────┐                         └──────────────┘
    │    │Streamlit │                   ┌──────────────┐
    │    │Container │                   │Streamlit     │
    │    ├──────────┤                   │Container     │
    │    │Web App   │                   ├──────────────┤
    │    │Python    │                   │Web App       │
    │    │3.9       │                   │Service       │
    │    └──────────┘                   └──────────────┘
    │
    └─ Volumes:
        ├─ ./dags:/opt/airflow/dags (code Airflow)
        ├─ ./scripts:/opt/airflow/scripts (scrapers)
        ├─ ./spark_jobs:/opt/spark/spark_jobs (ingestion)
        ├─ ./dbt_project:/opt/airflow/dbt_project (transformation)
        └─ ./data:/opt/airflow/data (files CSV)
```

---

## Performance & Scaling

### Volumes typiques par exécution

```
Nombre de produits scrappés:
- eBay:         1.2k-1.5k produits
- Leboncoin:    1.8k-2.2k produits
- Amazon:       100-200 produits
- CashExpress:  400-600 produits
─────────────────────────────────
TOTAL:          3.5k-4.5k produits par jour

Durée pipeline complet:
├─ Scraping:            2-3 minutes
├─ Spark ingestion:     1-2 minutes
├─ dbt transformation:  0.5-1 minute
├─ Telegram alert:      < 10 secondes
─────────────────────────────────
TOTAL:                  5-7 minutes
```

### Évolution des données

```
Jour 1:  4k produits
Jour 2:  4k + 4k = 8k (après dédup)
Jour 3:  8k + 4k = 12k
...
Semaine: ~28k produits (historique complet)

PostgreSQL Storage:
- Jour 1:  ~10 MB
- Semaine: ~100 MB
- Mois:    ~400 MB
- Année:   ~5 GB (avec index)

→ Totalement gérable sur une machine standard
```

---

## Sécurité: Flux d'Authentification

```
User → Airflow UI (8081)
          │
          ├─ Login: admin / AIRFLOW_ADMIN_PASSWORD
          │   (Stocké dans PostgreSQL Airflow)
          │
          └─ Access Control:
                ├─ Peut voir DAG
                ├─ Peut déclencher DAG
                └─ Peut voir logs (avec secrets masqués)

Airflow → PostgreSQL Data
          │
          └─ Connection String:
                postgresql://POSTGRES_DB_USER:POSTGRES_DB_PASSWORD@postgres_data:5432/smart_buy_db
                (Stocké en env var, pas en dur)

Airflow → Telegram
          │
          └─ Bot Token: ${TELEGRAM_TOKEN}
                Chat ID: ${TELEGRAM_CHAT_ID}
                (Env vars, pas en dur)

Streamlit → PostgreSQL
            │
            └─ Lecture seule (SELECT)
                DB_URL depuis env var
```

---

## Monitoring & Observabilité

### Logs Airflow

```
/opt/airflow/logs/
│
└─ dag_id=smart_buy_sentinel_pipeline/
   │
   └─ run_id=manual__2026-05-20T14:30:00/
      │
      ├─ scrape_ebay/
      │  └─ attempt_1.log
      │
      ├─ scrape_amazon/
      │  └─ attempt_1.log
      │
      ├─ spark_load_to_postgres/
      │  └─ attempt_1.log
      │
      ├─ dbt_transformation_shopping/
      │  └─ dbt.log
      │
      └─ send_deals_telegram/
         └─ attempt_1.log
```

### Métriques à monitorer

```
✅ Nombre de produits par jour (trend up = bon)
✅ Prix moyen par catégorie (stability = bon)
✅ Deal frequency (should find 2-5 deals/jour)
✅ Pipeline duration (< 10 min = acceptable)
✅ Data freshness (< 24h = bon)
❌ Erreurs scraping (0 = parfait)
❌ PostgreSQL errors (0 = parfait)
```

---

**Fin de la documentation architecturale**

Pour l'installation, consultez README.md ou QUICK_START.md.
