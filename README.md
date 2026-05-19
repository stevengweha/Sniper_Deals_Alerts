# 🎯 Smart Buy Sentinel - Architecture Pipeline Complet

![Smart Buy Sentinel Pipeline](Pipeline.jpeg)

---

## 📊 Vue d'ensemble du projet

**Smart Buy Sentinel** est un système **intelligent et automatisé** de monitoring des prix e-commerce qui scrape les plus grandes plateformes de vente d'occasion en ligne, classe les produits automatiquement, analyse les tendances de marché et alerte l'utilisateur sur les meilleures affaires.

### ✨ Valeur Ajoutée

| Fonctionnalité | Bénéfice |
|---|---|
| 🤖 **Scraping multi-sources** | Récupère les prix depuis eBay, Leboncoin, Amazon, CashExpress en temps réel |
| 🏷️ **Classification intelligente** | Classifie automatiquement 240+ types de produits avec IA contextuelle (6-couches de logique) |
| 📈 **Analyse statistique** | Calcule Z-scores, écarts de prix, estimations de revente par catégorie/condition |
| 🚨 **Alertes automatiques** | Envoie les **meilleures affaires** via Telegram en temps réel |
| 📊 **Dashboard Streamlit** | Visualise les deals en direct avec graphiques interactifs et filtres avancés |
| ⚙️ **Orchestration Airflow** | Exécute l'intégralité du pipeline **automatiquement chaque jour** |
| 🗄️ **Data Warehouse** | Stocke toutes les données structurées dans PostgreSQL pour l'historique |

---

## 🏗️ Architecture Technique Complète

### **Étage 1 : Ingestion RAW (Data Layer)**

```
📱 eBay → CSV Raw
📦 Leboncoin → CSV Raw
🛍️ Amazon → CSV Raw  
💳 CashExpress → CSV Raw
           ↓
    [Data/Processed/Used-Data-Shop/]
```

Les **4 scraper Python** (parallélisés) récupèrent les annonces et génèrent des fichiers CSV horodatés :
- `20260520_142530_ebay_search_tele.csv`
- `20260520_142532_lbc_search_tele.csv`
- etc.

**Technologie** : BeautifulSoup4 + Requests (scraping) + Cloudscraper (anti-bot)

---

### **Étage 2 : Orchestration (Airflow DAG)**

```
Apache Airflow (sur Docker) Lance le DAG "smart_buy_sentinel_pipeline"
              ↓
    ┌─────────┼─────────────┐
    ↓         ↓             ↓
scrape_ebay scrape_amazon scrape_cashexpress scrape_leboncoin
    ↓         ↓             ↓                 ↓
    └─────────┴─────────────┴─────────────────┘
              ↓
       spark_load_to_postgres
              ↓
    dbt_transformation_shopping
              ↓
       send_deals_telegram
```

**Cron** : `43 5 * * *` = Chaque jour à 7h43 (Europe/Paris)

**Paramètres** : Recherche dynamique (ex: "console", "smartphone", "PS5")

---

### **Étage 3 : Ingestion Spark (Data Processing)**

```
Spark Job (load_to_postgres.py)
    ↓
1️⃣ Lit CSV brut → DataFrame
2️⃣ Ajoute métadonnées (search_keyword, timestamp)
3️⃣ Écrit dans PostgreSQL (APPEND mode)
4️⃣ Archive CSV → /data/processed/used-data-shop/
```

**Technologie** : PySpark + PostgreSQL JDBC Driver

**Résultat** : Tables RAW dans PostgreSQL
- `raw_ebay` (3000+ lignes)
- `raw_leboncoin` (2500+ lignes)
- `raw_cashexpress` (1200+ lignes)
- `raw_amazon` (100+ lignes)

---

### **Étage 4 : Transformation dbt (Data Warehouse)**

dbt (Data Build Tool) **transforme les données brutes** en données exploitables via SQL :

```
dbt Staging Layer
├─ stg_ebay.sql          → Normalise prix, extrait marque
├─ stg_leboncoin.sql     → Gère formats français (1.299,99€)
├─ stg_cashexpress.sql   → Corrige état (Neuf/Occasion)
└─ stg_amazon.sql        → Unifie schéma
      ↓
dbt Intermediate Layer
└─ int_classified_products.sql
   ├─ 6-Layer Classification Logic
   │  ├─ LAYER 1: 100+ hardcoded patterns (marques smartphones, modèles consoles)
   │  ├─ LAYER 1-SPÉCIFIQUES: Jeux (Anno 1800), Magazines (Télé Poche), Accessoires
   │  ├─ LAYER 2: CSV rules (240+ mappings avec priorité)
   │  ├─ LAYER 3: Context fallbacks (prix, recherche)
   │  └─ LAYERS 4-6: Fallback chain
   ├─ Parsing intelligent : "🕹️ Console Nintendo DS" → category: "🕹️ Console", type: "Nintendo DS"
   └─ Output: sub_category, category, type
      ↓
dbt Marts Layer
└─ final_data.sql
   ├─ Déduplication temporelle (garder 1 seul exemplaire par produit)
   ├─ Statistiques par CATEGORY + ETAT (volume, prix médian, volatilité)
   ├─ Calcul Z-scores (anomalies de prix)
   ├─ Détection DEALS : "💎 ANOMALIE", "🔥 EXCELLENT", "❌ SURÉVALUÉ", "📊 NORMAL"
   ├─ Status operationnel : "🚨 SNIPER", "💤 OBSOLÈTE", "🟢 STABLE"
   └─ Tri : Meilleurs deals en premier
```

**Résultat Final** : Table `public_shopping.final_data` avec 40+ colonnes analytiques

---

### **Étage 5 : Alertes (Telegram Bot)**

```
send_deals.py
   ↓
SELECT * FROM final_data WHERE deal_score LIKE '💎%' OR deal_score LIKE '🔥%'
   ↓
Formate message → Telegram Chat
   ↓
👤 Utilisateur reçoit : 
   "🔥 EXCELLENT DEAL: iPhone 14 Pro → 450€ (prix marché: 650€) ✅"
```

---

### **Étage 6 : Visualisation (Streamlit)**

```
Streamlit Web App (Port 8501)
     ↓
Multi-pages:
├─ 🎯 Home: Bienvenue + stats
├─ 🛒 Shopping: 
│   ├─ Filtres (Category, Type, Deal Score)
│   ├─ Graphiques (Prix par Category, Volume, Tendances)
│   └─ Table interactive (tous les produits)
└─ 🚆 Transport: Données SNCF (autre pipeline)
```

---

## 🚀 Installation Complète (Débutant → Production)

### **Pré-requis Système**

```
✅ Docker Desktop (v20+)
✅ Docker Compose (v1.29+)
✅ Git
✅ 16 GB RAM minimum
✅ 20 GB disque libre
✅ OS: Windows, macOS, Linux
```

**Vérifier Installation** :
```powershell
docker --version         # Docker version 20.10+
docker-compose --version # Docker Compose version 1.29+
```

---

### **ÉTAPE 1 : Cloner le projet**

```bash
git clone https://github.com/votreusername/smart-buy-sentinel.git
cd smart-buy-sentinel
```

---

### **ÉTAPE 2 : Créer le fichier `.env` (CRITIQUE ⚠️)**

Crée un fichier `.env` à la racine du projet avec :

```env
# =========== AIRFLOW ===========
AIRFLOW_UID=50000
AIRFLOW_DB_PASSWORD=votre_mot_de_passe_secure_123
AIRFLOW__WEBSERVER__SECRET_KEY=votre_clé_secrète_airflow_32_caractères_min_abcd1234567890
AIRFLOW_ADMIN_PASSWORD=admin123

# =========== POSTGRESQL ===========
POSTGRES_DB_USER=smart_buy_user
POSTGRES_DB_PASSWORD=postgres_secure_password_123
DB_URL=postgresql://smart_buy_user:postgres_secure_password_123@postgres_data:5432/smart_buy_db

# =========== TELEGRAM (OPTIONNEL) ===========
TELEGRAM_TOKEN=123456789:ABCDefGHijKlMnOpQrStUvWxYz123456789
TELEGRAM_CHAT_ID=987654321

# =========== TIMEZONE ===========
TZ=Europe/Paris
```

**⚠️ IMPORTANT** : 
- Remplacez les mots de passe par les **vôtres**
- Ne commitez **JAMAIS** ce fichier (déjà dans `.gitignore`)
- Gardez-le **sécurisé** (permissions 600 sur Linux)

---

### **ÉTAPE 3 : Construire les images Docker**

```bash
docker-compose build
```

Cela construit 2 images :
1. **airflow-webserver** : Airflow + dbt + Spark + Python deps
2. **postgres_data** : PostgreSQL 13 Alpine

⏱️ **Durée** : 2-5 minutes (première fois)

---

### **ÉTAPE 4 : Démarrer les services**

```bash
docker-compose up -d
```

Cela crée 8 conteneurs :
```
✅ airflow-db         (PostgreSQL pour Airflow)
✅ airflow-init       (Initialisation)
✅ airflow-webserver  (UI http://localhost:8081)
✅ airflow-scheduler  (Orchester le DAG)
✅ postgres_data      (DB métier sur :5432)
✅ spark-master       (Coordinateur Spark)
✅ spark-worker       (Worker Spark)
✅ webapp             (Streamlit sur :8501)
```

**Vérifier le démarrage** :
```bash
docker-compose ps
```

**Attendre 30-60 secondes** (initialisation des bases de données)

---

### **ÉTAPE 5 : Accéder aux interfaces**

| Service | URL | Identifiants |
|---------|-----|---|
| **Airflow** | http://localhost:8081 | admin / admin123 |
| **Streamlit** | http://localhost:8501 | N/A (web public) |
| **PostgreSQL** | localhost:5432 | smart_buy_user / postgres_secure_password_123 |
| **Spark Master UI** | http://localhost:8082 | N/A (monitoring) |

---

## 🎮 Utilisation - Mode Execution

### **Option A : Exécuter le DAG via Airflow UI**

1. Ouvrir **http://localhost:8081**
2. Login : `admin` / `admin123`
3. Aller dans **DAGs** → `smart_buy_sentinel_pipeline`
4. Cliquer **Trigger DAG** (bouton play)
5. (OPTIONNEL) Ajouter paramètres JSON :
   ```json
   {
     "search_query": "PS5"
   }
   ```
6. Attendre **3-5 minutes** pour que le DAG s'exécute
7. Vérifier les logs via le **Tree View**

---

### **Option B : Exécuter via terminal (Docker)**

```bash
# Déclencher le DAG avec paramètres
docker-compose exec airflow-webserver \
  airflow dags trigger smart_buy_sentinel_pipeline \
  --conf '{"search_query": "console"}'

# Surveiller les logs
docker-compose exec airflow-scheduler \
  tail -f /opt/airflow/logs/dag_id=smart_buy_sentinel_pipeline/*/
```

---

### **Option C : Exécuter dbt manuellement (transformation uniquement)**

```bash
# Entre dans le conteneur Airflow
docker-compose exec airflow-webserver bash

# À l'intérieur du conteneur :
cd /opt/airflow/dbt_project

# Exécuter dbt
dbt run --select shopping      # Exécute tous les modèles shopping
dbt test --select shopping     # Teste les modèles
dbt seed --select mapping_sub_categories  # Recharge les seeds
```

---

### **Visualiser les résultats dans Streamlit**

1. Ouvrir **http://localhost:8501**
2. Navigation latérale → **Shopping**
3. Filtrer par catégorie, type, deal score
4. **Explorer les données en temps réel** 📊

---

## 📁 Structure du Projet

```
smart_buy_sentinel/
│
├── 📄 README.md                    (Ce fichier)
├── 📄 docker-compose.yml           (Orchestration Docker)
├── 📄 Dockerfile                   (Image Airflow custom)
├── 📄 .env.example                 (Template variables)
├── 📄 .env                         (⚠️ GIT IGNORED - À créer)
├── 📄 requirements.txt             (Dependencies Python)
│
├── 🗂️ dags/                        (Airflow DAGs)
│   ├── smart_buy_pipeline.py       (DAG principal - Orchestration)
│   └── dag_transport_train.py      (DAG transport - Bonus)
│
├── 🗂️ scripts/                     (Scripts Python)
│   ├── ebay_scraper.py            (Scrape eBay)
│   ├── leboncoin_scraper.py       (Scrape LeBonCoin)
│   ├── amazon_scraper.py          (Scrape Amazon)
│   ├── cashexpress_scraper.py     (Scrape CashExpress)
│   └── send_deals.py              (Telegram alerts)
│
├── 🗂️ spark_jobs/                  (PySpark jobs)
│   ├── load_to_postgres.py        (Ingestion PostgreSQL)
│   └── load_sncf_*.py             (Data transport)
│
├── 🗂️ dbt_project/                 (Data Build Tool)
│   ├── dbt_project.yml            (Config dbt)
│   ├── profiles.yml               (Profils connexion)
│   ├── 🗂️ models/
│   │   └── shopping/
│   │       ├── staging/           (Couche de nettoyage)
│   │       │   ├── stg_ebay.sql
│   │       │   ├── stg_leboncoin.sql
│   │       │   ├── stg_cashexpress.sql
│   │       │   └── stg_amazon.sql
│   │       ├── intermediate/      (Couche de logique)
│   │       │   └── int_classified_products.sql  (✨ Classification 6-couches)
│   │       └── marts/             (Couche output)
│   │           └── final_data.sql (🎯 Produit final)
│   │
│   ├── 🗂️ seeds/                   (Données de référence)
│   │   └── shopping/
│   │       └── mapping_sub_categories.csv (240+ patterns)
│   │
│   └── 🗂️ target/                  (GIT IGNORED - Artifacts dbt)
│       ├── compiled/
│       ├── run/
│       └── manifest.json
│
├── 🗂️ streamlit-app/               (Visualisation web)
│   ├── app_web.py                 (App principale)
│   └── pages/                     (Multi-pages)
│
├── 🗂️ data/                        (GIT IGNORED - Données)
│   ├── raw/
│   │   ├── shopping/              (Données brutes scraping)
│   │   └── transport-train/
│   │
│   └── processed/
│       └── used-data-shop/        (📍 CSV de sortie Spark)
│           └── .gitkeep
│
├── 🗂️ drivers/                     (JDBC drivers)
│   └── postgresql-42.2.29.jre7.jar
│
├── 🗂️ logs/                        (GIT IGNORED - Logs Airflow)
│   └── dag_id=smart_buy_sentinel_pipeline/
│       └── run_id=manual__2026-05-20T.../
│
└── 🗂️ .gitignore                   (Fichiers à ignorer)
```

---

## 🔧 Configuration Détaillée

### **dbt Profiles (Connexion PostgreSQL)**

Éditer `dbt_project/profiles.yml` :

```yaml
smart_buy:
  target: dev
  outputs:
    dev:
      type: postgres
      host: postgres_data          # Nom du service Docker
      user: smart_buy_user
      password: postgres_secure_password_123
      port: 5432
      dbname: smart_buy_db
      schema: public_shopping      # Schéma principal
      threads: 4
      keepalives_idle: 0
```

---

### **Airflow Variables (DAG Parameters)**

Dans **http://localhost:8081** :
- Admin → Variables
- Créer variable clé=`SEARCH_KEYWORDS` valeur=`console,smartphone,PS5`

---

### **Postgres : Créer la base manuellement (si nécessaire)**

```bash
docker-compose exec postgres_data psql -U smart_buy_user -d smart_buy_db

-- SQL Commands
CREATE SCHEMA IF NOT EXISTS public_shopping;
\dt public_shopping.*
SELECT COUNT(*) FROM raw_ebay;
```

---

## 🐛 Troubleshooting

### **Problème : Airflow ne démarre pas**

```bash
# Vérifier les logs
docker-compose logs airflow-webserver

# Redémarrer
docker-compose down
docker-compose up -d --force-recreate
```

---

### **Problème : PostgreSQL rejette les connexions**

```bash
# Vérifier le port
docker ps | grep postgres

# Vérifier les credentials dans .env
docker-compose exec postgres_data \
  psql -U smart_buy_user -d smart_buy_db -c "SELECT 1"
```

---

### **Problème : Spark job échoue**

```bash
# Vérifier les logs Spark
docker-compose logs spark-master
docker-compose logs spark-worker

# Vérifier JDBC driver
docker-compose exec airflow-webserver \
  ls -la /opt/spark/drivers/
```

---

### **Problème : dbt compile error**

```bash
# Entrer dans le conteneur
docker-compose exec airflow-webserver bash

# Vérifier la syntaxe dbt
cd /opt/airflow/dbt_project
dbt parse   # Compile models
dbt debug   # Teste connexions
```

---

### **Problème : Les CSV ne sont pas ingérés**

```bash
# Vérifier les CSV existent
docker-compose exec airflow-webserver \
  ls -la /opt/airflow/data/processed/used-data-shop/

# Lancer manuellement le scraper
docker-compose exec airflow-webserver \
  python /opt/airflow/scripts/ebay_scraper.py "PS5"
```

---

## 📊 Exemples de Requêtes

### **Voir les 10 meilleures affaires**

```sql
SELECT 
  title, 
  price, 
  category, 
  deal_score, 
  estimated_resell_profit
FROM public_shopping.final_data
WHERE deal_score LIKE '💎%' OR deal_score LIKE '🔥%'
ORDER BY estimated_resell_profit DESC
LIMIT 10;
```

### **Analysé les prix PS5 par vendeur**

```sql
SELECT 
  source,
  COUNT(*) as nb_annonces,
  AVG(price) as prix_moyen,
  MIN(price) as prix_min,
  MAX(price) as prix_max
FROM public_shopping.final_data
WHERE category LIKE '%PS5%'
  AND etat = 'Occasion'
GROUP BY source
ORDER BY prix_moyen ASC;
```

### **Détecter les anomalies (surévalué)**

```sql
SELECT 
  title, 
  price, 
  median_market_price,
  ROUND(((price - median_market_price) / median_market_price * 100)::numeric, 2) as pct_above_market
FROM public_shopping.final_data
WHERE price > (median_market_price * 1.5)
  AND market_volume > 10
ORDER BY pct_above_market DESC
LIMIT 20;
```

---

## 🎯 Workflow Complet - De A à Z

```
1. 🌅 05:43 → Airflow déclenche le DAG
        ↓
2. 🕷️ Scrapers lancent en parallèle (4 sources)
        ↓
3. 📁 CSV générés dans data/processed/used-data-shop/
        ↓
4. ⚡ Spark job lit CSV → PostgreSQL raw_*
        ↓
5. 🔄 dbt staging nettoie et normalise
        ↓
6. 🧠 dbt intermediate applique 6-couches de classification
        ↓
7. 📊 dbt marts agrège statistiques + décisions
        ↓
8. 🚨 send_deals.py envoie top 5 deals via Telegram
        ↓
9. 📈 Streamlit app affiche les résultats en live
        ↓
10. 💾 Données archivées pour historique/ML futur
```

---

## 🔐 Sécurité & Bonnes Pratiques

| ✅ À FAIRE | ❌ À ÉVITER |
|---|---|
| Stocker `.env` localement | Commiter `.env` dans Git |
| Utiliser des mots de passe **forts** (16+ chars) | Utiliser des mots de passe simples |
| Limiter l'accès Airflow avec auth | Exposer Airflow publiquement |
| Chiffrer les credentials Telegram | Stocker tokens en clair |
| Monitorer les logs Airflow | Ignorer les erreurs |
| Mettre à jour les images Docker régulièrement | Utiliser des versions obsolètes |

---

## 🚀 Déploiement en Production

### **Sur Cloud (AWS/GCP/Azure)**

```bash
# 1. Créer une VM ou Kubernetes cluster
# 2. Installer Docker + Docker Compose
# 3. Cloner le repo
# 4. Adapter .env pour cloud (RDS PostgreSQL, etc.)
# 5. docker-compose up -d
```

### **Avec Kubernetes (scalable)**

```bash
# Convertir Docker Compose en Helm charts
kompose convert -f docker-compose.yml -o ./helm

# Déployer sur k8s
helm install smart-buy-sentinel ./helm
```

---

## 📚 Documentation Complète

- **Airflow** : https://airflow.apache.org/docs/
- **dbt** : https://docs.getdbt.com/
- **Spark** : https://spark.apache.org/docs/
- **PostgreSQL** : https://www.postgresql.org/docs/
- **Streamlit** : https://docs.streamlit.io/

---

## 🤝 Support & Contribution

**Besoin d'aide ?**
- Consultez les **logs Docker** : `docker-compose logs -f [service]`
- Vérifiez la section **Troubleshooting** ci-dessus
- Ouvrez une **Issue** sur GitHub

**Contribuer au projet ?**
1. Fork le repo
2. Créer une branche (`git checkout -b feature/amazing-feature`)
3. Commit (`git commit -m 'Add amazing feature'`)
4. Push (`git push origin feature/amazing-feature`)
5. Ouvrir une Pull Request

---

## 📄 License

MIT License - Voir [LICENSE](LICENSE) pour détails

---

## 👨‍💻 Auteur

**Smart Buy Sentinel** - Système automatisé de monitoring e-commerce

Créé avec ❤️ pour les traders avertis et data enthusiasts

**Dernière mise à jour** : Mai 2026

---

## 🎓 Concepts Clés Expliqués

### **dbt 6-Layer Classification**

Pour chaque produit, dbt applique **6 couches** de logique pour déterminer sa catégorie :

```
LAYER 1:     100+ hardcoded patterns (marques, modèles)
LAYER 1-SPÉ: Jeux spécifiques, magazines, accessoires
LAYER 1.5:   Packs, PC gaming
LAYER 2:     240+ CSV rules avec priorité numérique
LAYER 3:     Fallbacks contextuels (prix, recherche)
LAYER 4-6:   Chaîne de secours générique
```

**Exemple** : "JEU PS5 ANNO 1800"
```
Teste LAYER 1 → %ps5% match! → Mais continue (pas spécifique)
Teste LAYER 1-SPÉ → %anno 1800% match! → GAGNANT → Classé "💿 Jeu Vidéo"
(N'évalue pas LAYER 2+ car déjà match)
```

---

### **Z-Score (Détection Anomalies)**

```
Z-Score = (Prix du produit - Prix moyen) / Écart-type
```

- **Z < -2** : Prix anormalement bas = 💎 DEAL
- **Z > 2** : Prix anormalement haut = ❌ SURÉVALUÉ
- **-2 ≤ Z ≤ 2** : Prix normal = 📊 MARCHÉ

---

## 📞 Contact

Pour questions/suggestions : [Email de contact à ajouter]

---

**Bienvenue dans Smart Buy Sentinel! 🎉**

