# 🚀 Smart Buy Sentinel

**Telegram Mini App pour le flipping d'objets électroniques** avec AI-powered deal scoring.

## 📋 Table des matières

- [Stack Technologique](#stack-technologique)
- [Architecture](#architecture)
- [Installation](#installation)
- [Configuration](#configuration)
- [Développement](#développement)
- [Déploiement](#déploiement)
- [API & Data Flow](#api--data-flow)
- [FAQ](#faq)

---

## 🛠 Stack Technologique

| Layer | Technologie | Version |
|-------|-------------|---------|
| **Frontend** | Next.js 14 (App Router) | ^14.2.0 |
| **Styling** | Tailwind CSS | ^3.4.3 |
| **Database** | MongoDB Atlas | - |
| **ORM** | Mongoose | ^8.4.1 |
| **Telegram** | @twa-dev/sdk | ^6.9.0 |
| **Icons** | Lucide React | ^0.408.0 |
| **Runtime** | Node.js | ^18.x |

---

## 🏗 Architecture

### Structure des dossiers

```
d:\FRONT_SNIPER_DEALS/
├── /app                      # Next.js App Router
│   ├── layout.tsx           # Layout principal + TelegramProvider
│   ├── page.tsx             # Page d'accueil
│   └── globals.css          # Styles globaux
├── /components              # Composants React
│   ├── DealCard.tsx         # Carte produit individuelle
│   ├── DealList.tsx         # Conteneur de la liste
│   ├── DealSkeleton.tsx     # Skeleton screens
│   ├── CategoryFilter.tsx   # Barre de filtrage sticky
│   ├── RefreshButton.tsx    # Bouton FAB de rafraîchissement
│   └── TelegramProvider.tsx # Context Telegram + SDK
├── /lib
│   └── mongodb.ts           # Gestion connexion MongoDB avec cache
├── /models
│   └── Deal.ts              # Schéma Mongoose + Types TypeScript
├── /actions
│   └── deals.ts             # Server Actions pour data fetching
├── /public
│   ├── manifest.json        # PWA Manifest
│   └── icon.png             # App Icon
├── package.json
├── tsconfig.json
├── tailwind.config.ts
├── next.config.ts
├── postcss.config.js
└── .env.local.example       # Variables d'environnement
```

### Data Flow

```
┌─────────────────────────┐
│   Python/Airflow        │  ← Scrape Idealo + Leboncoin
│   Infrastructure        │  ← Calcule Z-Score + Profit Margin
└────────────┬────────────┘
             │
             ▼
    ┌────────────────────┐
    │  MongoDB Atlas     │  ← Collection: "deals"
    │  (Stored Deals)    │
    └─────────┬──────────┘
              │
              ▼
    ┌────────────────────────────┐
    │  Next.js Server Action     │
    │  getDeals(category: str)   │
    │  - Tri: profit_margin DESC │
    │  - Cache: revalidateTag    │
    └─────────┬──────────────────┘
              │
              ▼
    ┌─────────────────────────┐
    │  Client Components      │
    │  - DealList             │
    │  - DealCard (Colored)   │
    │  - CategoryFilter       │
    │  - RefreshButton        │
    └─────────┬───────────────┘
              │
              ▼
    ┌─────────────────────────┐
    │  Telegram Mini App      │
    │  (User's Mobile)        │
    └─────────────────────────┘
```

---

## 📦 Installation

### Prérequis

- **Node.js** ≥ 18.x
- **npm** ou **yarn**
- **MongoDB Atlas** account (ou MongoDB local)
- **Telegram Bot Token** (optionnel)

### Étapes

```bash
# 1. Cloner/Naviguer au projet
cd d:\FRONT_SNIPER_DEALS

# 2. Installer les dépendances
npm install

# 3. Copier le fichier .env.local
cp .env.local.example .env.local

# 4. Remplir les variables d'environnement
# Éditer .env.local avec vos credentials MongoDB
```

---

## ⚙️ Configuration

### Variables d'Environnement (.env.local)

```env
# ✅ OBLIGATOIRE
MONGODB_URI=mongodb+srv://username:password@cluster.mongodb.net/sniper_deals?retryWrites=true&w=majority

# Optionnel
NODE_ENV=development
TELEGRAM_BOT_TOKEN=your_bot_token_here
```

### MongoDB Atlas Setup

1. **Créer un cluster** : [MongoDB Atlas Console](https://cloud.mongodb.com)
2. **Créer une database** : `sniper_deals`
3. **Créer une collection** : `deals`
4. **Générer un connection string** :
   - Network Access → Ajouter votre IP
   - Database Users → Créer un utilisateur
   - Connect → Copier la connection string

### Schéma des Deals (MongoDB)

```javascript
{
  _id: ObjectId,
  title: String,                    // Titre du produit
  category: "Smartphones|Consoles|Laptops|Other",
  current_price: Number,            // Prix actuel (EUR)
  idealo_price: Number,             // Prix de référence Idealo
  profit_margin: Number,            // % de profit = ((idealo - current) / current) * 100
  z_score: Number,                  // Score de profitabilité (AI)
  source: "Idealo|Leboncoin",
  url: String,                      // Lien direct au produit
  image_url: String,
  product_id: String (unique),
  availability: "In Stock|Low Stock|Out of Stock",
  stock_quantity: Number,
  created_at: Date,
  scraped_at: Date,
  confidence_score: Number (0-100),
  location: String,                 // Pour Leboncoin
  seller_rating: Number (0-5),
  last_updated: Date
}
```

---

## 💻 Développement

### Démarrer le serveur local

```bash
npm run dev
```

Ouvrir : http://localhost:3000

### Mode développement Telegram

Pour tester en mode local sans Telegram:
1. Le `TelegramProvider` gère les erreurs gracieusement
2. Les données mock peuvent être injectées en dev
3. Vérifier la console pour les logs de connexion Telegram

### TypeScript Checking

```bash
npm run type-check
```

### Build local

```bash
npm run build
npm start
```

---

## 🌐 Déploiement

### Vercel (Recommandé pour Telegram Mini Apps)

```bash
# 1. Installer Vercel CLI
npm i -g vercel

# 2. Déployer
vercel

# 3. Ajouter variables d'environnement dans Vercel dashboard
# - MONGODB_URI
# - NODE_ENV=production

# 4. Configurer dans Telegram Bot Settings
# Webhook URL: https://votre-app.vercel.app
```

### Dockerfile (Pour déploiement conteneurisé)

```dockerfile
FROM node:18-alpine

WORKDIR /app

COPY package*.json ./
RUN npm ci --only=production

COPY .next .next
COPY public public

EXPOSE 3000
CMD ["npm", "start"]
```

---

## 📡 API & Data Flow

### Server Actions Disponibles

#### `getDeals(category?: string): Promise<DealsResponse>`

Récupère les deals filtrés par catégorie.

```typescript
// Tous les deals triés par profit DESC
const response = await getDeals();

// Deals Smartphones uniquement
const response = await getDeals('Smartphones');

// Réponse
{
  success: boolean,
  data?: IDeal[],
  error?: string,
  count?: number,
  timestamp?: Date
}
```

#### `getDealById(dealId: string): Promise<DealsResponse>`

Récupère un deal spécifique.

```typescript
const response = await getDealById('507f1f77bcf86cd799439011');
```

#### `getDealStats(): Promise<{...}>`

Récupère les statistiques globales.

```typescript
const response = await getDealStats();
// Retourne: total, avgProfitMargin, bestDeal, byCategory
```

#### `refreshDeals(): Promise<{...}>`

Revalide le cache et force le rafraîchissement.

```typescript
const response = await refreshDeals();
// Message: "Données actualisées avec succès"
```

---

## 🎨 Design System

### Couleurs

| Usage | Couleur | Code |
|-------|---------|------|
| **Arrière-plan** | Slate-950 | `#0f172a` |
| **Profit Excellent** | Emerald-500 | `#10b981` |
| **Profit Bon** | Orange-500 | `#f97316` |
| **Profit Standard** | Slate-600 | `#475569` |

### Badge Profit - Logique Conditionnelle

```typescript
if (profit_margin >= 20) return "Vert (Excellent)";
if (profit_margin >= 10) return "Orange (Bon)";
return "Gris (Standard)";
```

---

## 📱 Telegram Mini App Integration

### Initialisation

```typescript
import WebApp from '@twa-dev/sdk';

// Dans TelegramProvider.tsx
WebApp.ready();
const user = WebApp.initDataUnsafe?.user;
WebApp.expand(); // Fullscreen
```

### Accès utilisateur

```typescript
const { user } = useTelegram();
// user.id, user.first_name, user.username, user.language_code
```

---

## 🔒 Sécurité

- ✅ Server Actions (exécutées côté serveur)
- ✅ MongoDB validation avec Mongoose
- ✅ CORS headers configurés
- ✅ Environment variables protégées
- ✅ Pas de credentials en frontend

---

## 🐛 Troubleshooting

### MongoDB Connection Timeout

```bash
# Vérifier la connection string
# Vérifier que votre IP est whitelistée dans Atlas
# Augmenter serverSelectionTimeoutMS dans mongodb.ts
```

### Styles Tailwind non appliqués

```bash
# Rebuilder les styles
npm run dev
# Vider cache Next.js
rm -rf .next
```

### Telegram Web App non chargé

```bash
# Vérifier que le script est chargé en layout.tsx
<script src="https://telegram.org/js/telegram-web-app.js" defer></script>

# Vérifier la console du navigateur
```

---

## 📊 Performance

- **Image optimization** : Gérée par Next.js
- **Code splitting** : Automatique avec App Router
- **Caching** : MongoDB + Next.js revalidateTag
- **Bundle size** : ~80KB gzipped

---

## 🚀 Features Futures

- [ ] Notifications push (Telegram API)
- [ ] Historique des deals
- [ ] Analytics utilisateur
- [ ] Filtres avancés (prix min/max)
- [ ] Partage deals via Telegram
- [ ] Dark/Light mode toggle

---

## 📄 Licence

MIT - Libre d'utilisation

---

## 🙋 Support

Pour toute question ou bug:
1. Vérifier les logs
2. Consulter [Next.js Docs](https://nextjs.org/docs)
3. Consulter [Mongoose Docs](https://mongoosejs.com)
4. Consulter [Telegram Mini App Docs](https://core.telegram.org/bots/webapps)

---

**Créé avec ❤️ pour les snipers de deals électroniques** ⚡
