# 🚀 Dashboard Streamlit - Guide de Lancement

## Installation

```bash
# Installez les dépendances
pip install -r requirements_dashboard.txt
```

## Configuration

Créez un fichier `.env` à la racine du projet :

```env
MONGODB_URI=mongodb+srv://your_username:your_password@cluster.mongodb.net/smart_buy?retryWrites=true&w=majority
```

## Lancement

```bash
# Lancer le dashboard
streamlit run dashboard_simplified.py
```

Le dashboard s'ouvrira sur `http://localhost:8501`

## Fonctionnalités

✅ **Filtres simplifiés** - Catégorie, Marque, Modèle, Prix, Profit  
✅ **KPIs essentiels** - Prix moyen, meilleur prix, gain moyen  
✅ **Affichage en cartes** - Facile à scanner pour les utilisateurs  
✅ **Tableau complet** - Vue d'ensemble de toutes les données  
✅ **Export CSV** - Téléchargement instantané  
✅ **Recherche texte** - Recherche libre par mots-clés  
✅ **Cache intelligent** - Actualisé tous les 5 minutes  

## Structure MongoDB Attendue

Collection `deals` avec les champs :
```javascript
{
  _id: ObjectId,
  url: String,
  title: String,
  brand: String,
  category: String,
  product_model: String,
  price: Number,
  estimated_resell_profit: Number,
  deal_score: String,
  operational_status: String,
  product_condition: String,
  source: String,
  data_age_hours: Number,
  // ... autres champs
}
```

## Conseils d'utilisation

🎯 **Pour les deals rentables** : Utilisez le filtre "Profit Minimum"  
📍 **Par catégorie** : Sélectionnez la catégorie dans la barre latérale  
🔍 **Recherche rapide** : Tapez des mots-clés (ex: "MacBook", "Pro")  
📥 **Export** : Téléchargez les résultats en CSV pour votre analyse
