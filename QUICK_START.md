# ⚡ Smart Buy Sentinel - Quick Start Guide

**Objectif** : Lancer l'app en 5 minutes! 🚀

---

## 1️⃣ Prérequis (2 min)

```bash
# Installer Node.js 18+ depuis https://nodejs.org/

# Vérifier
node --version
npm --version

# Créer account MongoDB Atlas (gratuit)
# https://www.mongodb.com/cloud/atlas
```

---

## 2️⃣ Setup du Projet (2 min)

```bash
# Naviguer au dossier
cd d:\FRONT_SNIPER_DEALS

# Installer les dépendances
npm install

# Attendre ~2-3 min (première fois)
```

---

## 3️⃣ Configuration MongoDB (1 min)

### Obtenir la Connection String

1. **MongoDB Atlas** : https://cloud.mongodb.com
2. **Clusters** → Sélectionner ton cluster
3. **Connect** → **Connect your application**
4. Copier la connection string

Format attendu :
```
mongodb+srv://YOUR_USERNAME:YOUR_PASSWORD@cluster0.mongodb.net/sniper_deals?retryWrites=true&w=majority
```

### Ajouter au Fichier .env.local

```bash
# Créer le fichier .env.local
cp .env.local.example .env.local

# Éditer avec ton éditeur favori
# (Remplacer YOUR_USERNAME, YOUR_PASSWORD, cluster0)
```

### Exemple (fictif) :
```env
MONGODB_URI=mongodb+srv://myuser:mypass123@cluster0.mongodb.net/sniper_deals?retryWrites=true&w=majority
NODE_ENV=development
```

---

## 4️⃣ Lancer le Serveur (Command)

```bash
npm run dev
```

**Output attendu** :
```
> next dev

  ▲ Next.js 14.2.0
  - Local:        http://localhost:3000
  - Environments: .env.local

✓ Ready in 2.5s
```

### Accéder à l'App

Ouvrir dans le navigateur : **http://localhost:3000**

---

## 5️⃣ Tester Rapidement

### ✅ Tester Localement

1. Ouvrir http://localhost:3000
2. Voir le message "Aucun deal trouvé" (normal, pas de data)
3. Cliquer les filtres de catégorie
4. Vérifier que ça réagit (console clean)

### ✅ Injecter de la Data (Optionnel)

Pour tester avec de vraies données, créer des deals dans MongoDB :

```javascript
// MongoDB Compass ou Atlas Web Console
// Insert into deals collection:

db.deals.insertMany([
  {
    title: "iPhone 15 256GB",
    category: "Smartphones",
    current_price: 850,
    idealo_price: 1099,
    profit_margin: 29.3,
    z_score: 3.45,
    source: "Idealo",
    url: "https://idealo.de/...",
    product_id: "iphone15-256",
    availability: "In Stock",
    created_at: new Date(),
    scraped_at: new Date()
  },
  {
    title: "PlayStation 5 Console",
    category: "Consoles",
    current_price: 420,
    idealo_price: 550,
    profit_margin: 30.95,
    z_score: 3.2,
    source: "Leboncoin",
    url: "https://leboncoin.fr/...",
    product_id: "ps5-standard",
    availability: "In Stock",
    created_at: new Date(),
    scraped_at: new Date()
  }
])
```

Puis rafraîchir la page → Les deals apparaissent! 🎉

---

## 🐛 Troubleshooting Rapide

### ❌ Erreur : "ENOENT: no such file or directory, open '.env.local'"

**Solution** :
```bash
cp .env.local.example .env.local
# Puis remplir MONGODB_URI
```

### ❌ Erreur : "Cannot connect to MongoDB"

**Solutions** :
```bash
# 1. Vérifier la connection string
# Format: mongodb+srv://USER:PASS@CLUSTER.mongodb.net/DATABASE

# 2. MongoDB Atlas: Network Access
# Settings → Network Access → Add IP → 0.0.0.0/0

# 3. Vérifier les credentials (USER, PASS)

# 4. Redémarrer le serveur
npm run dev
```

### ❌ Erreur : "Port 3000 already in use"

**Solution** :
```bash
# Option 1: Utiliser un autre port
npm run dev -- -p 3001

# Option 2: Tuer le processus existant
# Windows: taskkill /PID [PID] /F
# Mac/Linux: kill -9 [PID]
```

### ❌ Styles Tailwind pas appliqués

**Solution** :
```bash
# Arrêter le serveur (Ctrl+C)
rm -rf .next
npm run dev
```

---

## 📁 Structure du Projet

```
d:\FRONT_SNIPER_DEALS/
├── /app              ← Pages & Layout
├── /components       ← React Components
├── /lib              ← Utilitaires (MongoDB)
├── /models           ← Mongoose Schemas
├── /actions          ← Server Actions
├── /public           ← Assets statiques
├── package.json      ← Dépendances
├── .env.local        ← Secrets (ne pas commit!)
├── README.md         ← Documentation complète
├── FEATURES.md       ← Features list
└── DEPLOYMENT.md     ← Guide déploiement
```

---

## 📚 Ressources

| Resource | Lien |
|----------|------|
| **Next.js Docs** | https://nextjs.org/docs |
| **Tailwind CSS** | https://tailwindcss.com |
| **MongoDB** | https://docs.mongodb.com |
| **Telegram API** | https://core.telegram.org/bots/api |
| **TypeScript** | https://www.typescriptlang.org |

---

## 🎯 Prochaines Étapes

1. **Localiser** : Analyser les deals avec vraies données Airflow
2. **Customiser** : Ajouter ta logique métier personnalisée
3. **Déployer** : Voir [DEPLOYMENT.md](./DEPLOYMENT.md)
4. **Monitorer** : Setup logs & analytics

---

## 💡 Tips & Tricks

### Mode Dark Déjà Activé
```
L'app est en dark mode par défaut
Pas besoin de toggle!
```

### Hot Reload Fonctionne
```
Les changements en code se reflètent automatiquement
Appuyer F12 → Console pour vérifier les erreurs
```

### TypeScript Strict
```
Certaines erreurs seront affichées dans le terminal
C'est normal! Cela évite les bugs runtime
```

### Skeleton Screens
```
Voir les skeletons:
1. Ouvrir DevTools (F12)
2. Network → Slow 3G
3. Changer les filtres
```

---

## ✅ Checklist - Prêt pour Production?

- [ ] Node.js 18+ installé
- [ ] MongoDB Atlas cluster créé
- [ ] .env.local configuré
- [ ] `npm install` exécuté
- [ ] `npm run dev` fonctionne
- [ ] http://localhost:3000 accessible
- [ ] Pas d'erreurs dans la console
- [ ] Deals affichés (si data injectée)
- [ ] Les filtres fonctionnent
- [ ] Le bouton refresh fonctionne

Si tout est ✅ → **Tu es prêt pour développer!** 🚀

---

## 🆘 Besoin d'Aide?

1. Vérifier [README.md](./README.md) section "Troubleshooting"
2. Lire [ARCHITECTURE.md](./ARCHITECTURE.md) pour comprendre le flow
3. Ouvrir GitHub Issues (si applicable)
4. Checker la console du navigateur (F12)

---

**Happy Coding!** 💻⚡

*Créé pour les snipers de deals électroniques*
