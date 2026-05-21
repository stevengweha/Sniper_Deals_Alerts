# 📚 Smart Buy Sentinel - Index & Navigation

> **Guide complet pour naviguer dans le projet et ses ressources**

---

## 🚀 Points de Départ

| Objectif | Ressource | Temps |
|----------|-----------|-------|
| **Lancer rapidement** | [QUICK_START.md](./QUICK_START.md) | 5 min ⚡ |
| **Installer & configurer** | [README.md](./README.md) | 10 min 📋 |
| **Déployer en prod** | [DEPLOYMENT.md](./DEPLOYMENT.md) | 15 min 🚀 |
| **Comprendre l'architecture** | [ARCHITECTURE.md](./ARCHITECTURE.md) | 30 min 🏗️ |
| **Voir les features** | [FEATURES.md](./FEATURES.md) | 20 min ✨ |
| **Trouver une commande** | [COMMANDS.md](./COMMANDS.md) | 2 min 🛠️ |

---

## 📁 Structure du Projet

### 🎯 Frontend Code

```
/app
├── layout.tsx          → Root layout + TelegramProvider
├── page.tsx            → Homepage avec logique principale
└── globals.css         → Styles globaux + Tailwind
```

**Qu'est-ce que c'est ?**
- `layout.tsx` : Enveloppe tous les pages, setup PWA
- `page.tsx` : Composant principal, gère les filtres et appels API
- `globals.css` : Base styling + safe areas mobile

**Quand l'éditer ?**
- Ajouter une nouvelle page ? Créer `/app/[page]/page.tsx`
- Changer le layout ? Éditer `layout.tsx`
- Ajouter du CSS global ? Éditer `globals.css`

---

### 🧩 Components

```
/components
├── DealCard.tsx          → Affiche 1 deal (badge couleur)
├── DealList.tsx          → Liste des deals + stats
├── DealSkeleton.tsx      → Skeleton screens (loading)
├── CategoryFilter.tsx    → Filtres sticky (sticky top)
├── RefreshButton.tsx     → Bouton FAB refresh
└── TelegramProvider.tsx  → Context Telegram + SDK
```

**Qu'est-ce que c'est ?**
- **DealCard** : Carte individuelle avec badge profit coloré (>20% vert, 10-20% orange, gris)
- **DealList** : Affiche la liste + statistiques top 3
- **DealSkeleton** : Animation de chargement fluide
- **CategoryFilter** : Barre sticky pour filtrer par catégorie
- **RefreshButton** : Bouton flottant pour rafraîchir
- **TelegramProvider** : Setup Telegram SDK + hook `useTelegram()`

**Quand l'éditer ?**
- Ajouter un champ à la carte ? Éditer `DealCard.tsx`
- Changer les couleurs du badge ? Éditer `DealCard.tsx` → `getProfitColor()`
- Ajouter une stat à la liste ? Éditer `DealList.tsx`

---

### 🗄️ Data Layer

```
/lib
└── mongodb.ts          → Connexion MongoDB singleton + cache

/models
└── Deal.ts             → Mongoose schema + types TypeScript

/actions
└── deals.ts            → Server Actions pour data fetching
```

**Qu'est-ce que c'est ?**
- **mongodb.ts** : Gère la connexion à MongoDB avec caching (singleton pattern)
- **Deal.ts** : Définit le schéma des deals + indexes DB
- **deals.ts** : Server Actions pour `getDeals()`, `getDealStats()`, etc.

**Quand l'éditer ?**
- Ajouter un champ deal ? Éditer `Deal.ts` (schema + interface)
- Créer une nouvelle requête DB ? Créer une Server Action dans `deals.ts`
- Changer la logique de tri ? Éditer `deals.ts` → `getDeals()`

---

### ⚙️ Configuration

```
package.json            → Dépendances + scripts
tsconfig.json           → TypeScript config
next.config.ts          → Next.js optimisations
tailwind.config.ts      → Tailwind theme (dark mode)
postcss.config.js       → PostCSS setup
.env.local.example      → Template variables d'env
.gitignore              → Fichiers ignorés par git
```

**Qu'est-ce que c'est ?**
- **package.json** : Liste toutes les dépendances npm
- **tsconfig.json** : Configure TypeScript strict mode
- **next.config.ts** : Optimise la build, ajoute security headers
- **tailwind.config.ts** : Définie les couleurs (slate-950, emerald-500)
- **postcss.config.js** : Setup CSS post-processing

**Quand l'éditer ?**
- Ajouter une dépendance ? Éditer `package.json` (mieux: `npm install package`)
- Changer les couleurs Tailwind ? Éditer `tailwind.config.ts`

---

### 📚 Documentation

```
README.md               → Installation & guide complet
QUICK_START.md          → Démarrage en 5 min
ARCHITECTURE.md         → Deep dive technique
DEPLOYMENT.md           → Guide déploiement (Vercel + Docker)
FEATURES.md             → Toutes les features documentées
COMMANDS.md             → Commandes utiles
INDEX.md (ce fichier)   → Navigation du projet
```

---

## 🔗 Connexions Entre Fichiers

### User Interaction Flow

```
app/page.tsx (MAIN)
    ↓
    ├─→ CategoryFilter (user selects category)
    ├─→ DealList (displays data)
    │   └─→ DealCard x N (each deal)
    └─→ RefreshButton (user clicks refresh)

All connect to:
    ├─→ actions/deals.ts (Server Action)
    │   └─→ lib/mongodb.ts (DB connection)
    │       └─→ models/Deal.ts (schema)
    └─→ components/TelegramProvider.tsx (Telegram SDK)
```

### How to Trace a Feature

**Exemple: "L'utilisateur clique sur un deal"**

1. **UI Layer** → `DealCard.tsx`
   - Chercher `onClick={onDealClick?.(deal)}`
   - Prop `onDealClick` vient d'où ?

2. **Container** → `DealList.tsx`
   - Chercher `<DealCard ... onDealClick={...} />`
   - `onDealClick` reçu en prop

3. **Page** → `app/page.tsx`
   - Chercher `<DealList ... onDealClick={handleDealClick} />`
   - `handleDealClick` défini ici
   - Ouvre `window.open(deal.url)`

---

## 🛠️ Common Development Tasks

### ❓ "Je veux ajouter un nouveau filtre"

1. Éditer `CategoryFilter.tsx` → Ajouter option à `CATEGORIES`
2. Éditer `Deal.ts` → Ajouter field si nécessaire
3. Éditer `actions/deals.ts` → Mettre à jour `getDeals()` query

### ❓ "Je veux changer la couleur du badge"

1. Éditer `DealCard.tsx` → `getProfitColor()` function
2. Changer les valeurs de threshold (currently: 20%, 10%)

### ❓ "Je veux ajouter un stat à la liste"

1. Éditer `DealList.tsx` → Stats header section
2. Ajouter le calcul là ou dans `actions/deals.ts`

### ❓ "Je veux connecter une autre API"

1. Créer une Server Action dans `actions/[domain].ts`
2. Appeler depuis le composant
3. Gérer loading/error states

### ❓ "Je veux déployer en production"

1. Lire [DEPLOYMENT.md](./DEPLOYMENT.md)
2. Créer Vercel project
3. Ajouter `MONGODB_URI` en secret
4. Push sur GitHub → Auto-deploy

---

## 📊 File Sizes

| File | Size | Purpose |
|------|------|---------|
| lib/mongodb.ts | 2.5 KB | Connection mgmt |
| models/Deal.ts | 4.5 KB | Schema + types |
| actions/deals.ts | 5.5 KB | Data fetching |
| DealCard.tsx | 5.2 KB | UI component |
| DealList.tsx | 4.8 KB | Container |
| app/page.tsx | 3.8 KB | Main page |

**Total Code**: ~1500 lines (excluding docs)
**Total Docs**: ~1500 lines

---

## 🚀 Quick Navigation

### By Role

**🎨 Designer/Frontend Dev**
- [DealCard.tsx](./components/DealCard.tsx) - Styling
- [globals.css](./app/globals.css) - Theme
- [tailwind.config.ts](./tailwind.config.ts) - Colors

**🔧 Backend Dev**
- [mongodb.ts](./lib/mongodb.ts) - DB connection
- [Deal.ts](./models/Deal.ts) - Schema
- [deals.ts](./actions/deals.ts) - Queries

**🚀 DevOps**
- [DEPLOYMENT.md](./DEPLOYMENT.md) - Deploy guide
- [COMMANDS.md](./COMMANDS.md) - CLI commands
- [.env.local.example](./.env.local.example) - Config

**📚 Product Manager**
- [FEATURES.md](./FEATURES.md) - Feature list
- [README.md](./README.md) - Overview
- [ARCHITECTURE.md](./ARCHITECTURE.md) - How it works

---

## 🆘 Finding Code

### "Where is the profit calculation?"
```bash
# Grep search
grep -r "profit_margin" .
# Find: Deal.ts, DealCard.tsx, actions/deals.ts
```

### "How does Telegram integration work?"
```
components/TelegramProvider.tsx → useTelegram hook
app/layout.tsx → <TelegramProvider> wrapper
app/page.tsx → const { user } = useTelegram()
```

### "How are deals sorted?"
```
actions/deals.ts → .sort({ profit_margin: -1, z_score: -1 })
models/Deal.ts → indexes for optimization
DealList.tsx → displays in order
```

---

## 📋 Checklist Before Deployment

- [ ] Read [QUICK_START.md](./QUICK_START.md)
- [ ] Understand [ARCHITECTURE.md](./ARCHITECTURE.md)
- [ ] Test locally with `npm run dev`
- [ ] Check [DEPLOYMENT.md](./DEPLOYMENT.md)
- [ ] Setup MongoDB Atlas
- [ ] Configure Vercel secrets
- [ ] Deploy with `vercel --prod`

---

## 🎓 Learning Resources

### By Topic

**Next.js 14 App Router**
- Docs: https://nextjs.org/docs
- Related files: `app/`, `actions/`

**MongoDB + Mongoose**
- Docs: https://mongoosejs.com
- Related files: `lib/mongodb.ts`, `models/Deal.ts`

**Tailwind CSS**
- Docs: https://tailwindcss.com
- Related files: `globals.css`, `tailwind.config.ts`

**Telegram SDK**
- Docs: https://core.telegram.org/bots/webapps
- Related files: `components/TelegramProvider.tsx`

**TypeScript**
- Docs: https://www.typescriptlang.org
- Related files: All `.ts` and `.tsx` files

---

## 💡 Pro Tips

1. **Use `grep` to find code** → `grep -r "search-term" ./`
2. **Check types first** → `npm run type-check` before dev
3. **Read the console** → F12 → Console tab has useful logs
4. **Start with QUICK_START.md** → Fastest way to get running
5. **Architecture.md is your friend** → When confused, read it

---

## 📞 Need Help?

| Problem | Solution |
|---------|----------|
| Can't start dev server | Check [QUICK_START.md](./QUICK_START.md#troubleshooting-rapide) |
| MongoDB connection error | Read [README.md](./README.md#mongodb-atlas-setup) |
| Deployment issues | See [DEPLOYMENT.md](./DEPLOYMENT.md#troubleshooting-déploiement) |
| Want to add a feature | Check [FEATURES.md](./FEATURES.md#future-features) |
| Need a command | Search [COMMANDS.md](./COMMANDS.md) |

---

**Last Updated**: 21 mai 2026
**Version**: 1.0.0
**Status**: ✅ Production Ready

Made with ❤️ for deal snipers ⚡
