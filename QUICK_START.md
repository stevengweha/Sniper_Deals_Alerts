# 🚀 Quick Start - Démarrer en 5 minutes

Vous êtes pressé? Voici les **étapes essentielles** uniquement.

---

## ⚡ Installation Rapide (5 min)

### **1. Clone + Env Setup** (2 min)

```bash
git clone https://github.com/votreusername/smart-buy-sentinel.git
cd smart-buy-sentinel

# Copier le template env
cp .env.example .env

# Éditer .env - Changez MINIMALEMENT:
# - AIRFLOW_DB_PASSWORD → quelque chose
# - POSTGRES_DB_PASSWORD → quelque chose  
# - DB_URL → met à jour les passwords
# Les tokens Telegram sont optionnels
```

**Rapide** :
```bash
# Sans éditer manuellement:
sed -i 's/changez_moi/votre_password_123/g' .env
```

---

### **2. Lancer Docker** (3 min)

```bash
docker-compose build
docker-compose up -d

# Attendre 30 secondes...
docker-compose ps  # Vérifier que tout démarre
```

✅ **Tous les services sont prêts!**

---

## 🎮 Utiliser

### **Airflow DAG** 
- URL : http://localhost:8081
- Login : `admin` / `admin123` (ou votre AIRFLOW_ADMIN_PASSWORD)
- Cliquer le bouton **play** sur le DAG

### **Voir les résultats**
- URL : http://localhost:8501 (Streamlit)
- Page "Shopping" → Filtrer les deals

### **Base de données** (requêtes directes)
```bash
docker-compose exec postgres_data \
  psql -U smart_buy_user -d smart_buy_db

# Requête test:
SELECT COUNT(*) as total_produits FROM raw_ebay;
```

---

## 🔧 Commandes Essentielles

| Action | Commande |
|--------|----------|
| Voir les logs | `docker-compose logs -f airflow-webserver` |
| Arrêter tout | `docker-compose down` |
| Redémarrer | `docker-compose restart` |
| Nettoyer complètement | `docker-compose down -v` |
| Entrer dans Airflow | `docker-compose exec airflow-webserver bash` |

---

## 📊 Vérifier que ça marche

```bash
# 1. Tous les services UP?
docker-compose ps
# Les 8 services doivent avoir STATUS "Up"

# 2. Airflow accessible?
curl http://localhost:8081
# Doit retourner HTML

# 3. PostgreSQL répond?
docker-compose exec postgres_data \
  psql -U smart_buy_user -d smart_buy_db -c "SELECT 1"
# Doit afficher "1"

# 4. Spark workers online?
curl http://localhost:8082
# Doit voir "1 Worker(s)"
```

---

## ❌ Problème? 

### Quick Fixes

**Airflow crash au démarrage** :
```bash
docker-compose down
docker-compose up -d --force-recreate
docker-compose logs -f airflow-init
```

**PostgreSQL rejette connexion** :
```bash
# Vérifier credentials dans .env
cat .env | grep POSTGRES
docker-compose down postgres_data
docker-compose up -d postgres_data
```

**Rien ne marche** :
```bash
# Hard reset complet
docker-compose down -v  # ⚠️ EFFACE LES DONNÉES
docker-compose up -d
```

---

## 📖 Pour plus de détails

Consultez **README.md** (documentation complète)

---

**C'est fait!** 🎉 Vous avez Smart Buy Sentinel qui tourne!
