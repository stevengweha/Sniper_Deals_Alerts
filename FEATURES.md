# 🎯 Smart Buy Sentinel - Features Documentation

## Table des matières

- [Core Features](#core-features)
- [UI Components](#ui-components)
- [Data Features](#data-features)
- [Telegram Integration](#telegram-integration)
- [Future Features](#future-features)

---

## 🚀 Core Features

### 1. Deal Listing avec Tri Intelligent

**Description** : Affiche les deals triés par profitabilité (marge de profit décroissante).

**Implémentation** :
```typescript
// actions/deals.ts
const deals = await Deal.find(query)
  .sort({ profit_margin: -1, z_score: -1 })
  .limit(100)
  .lean()
  .exec();
```

**Bénéfices** :
- ✅ Les meilleurs deals en haut
- ✅ Décisions d'achat rapides
- ✅ Optimisé avec indexes MongoDB

**Exemple Data** :
```javascript
{
  title: "iPhone 15 256GB",
  current_price: 850,
  idealo_price: 1099,
  profit_margin: 29.3,  // (1099-850)/850 * 100
  z_score: 3.45,
  source: "Idealo"
}
```

---

### 2. Filtrage par Catégorie

**Description** : Changement de catégorie en temps réel (Smartphones, Consoles, Laptops).

**Flow** :
```
User clicks category
    ↓
CategoryFilter onChange fires
    ↓
useEffect in page.tsx triggered
    ↓
setSelectedCategory updates
    ↓
getDeals(category) called
    ↓
Skeleton shows while loading
    ↓
DealList re-renders with new data
```

**Catégories Disponibles** :
```typescript
type Category = 'All' | 'Smartphones' | 'Consoles' | 'Laptops';

const CATEGORIES = [
  { id: 'All', label: 'Tous', icon: '📦' },
  { id: 'Smartphones', label: '📱 Téléphones', icon: '📱' },
  { id: 'Consoles', label: '🎮 Consoles', icon: '🎮' },
  { id: 'Laptops', label: '💻 PC', icon: '💻' },
];
```

**Query** :
```typescript
if (category && category !== 'All') {
  query.category = category;
}
```

---

### 3. Badge de Profit Coloré Conditionnel

**Description** : Les cartes de deals affichent un badge avec une couleur en fonction de la marge de profit.

**Logique** :
```typescript
const getProfitColor = (profit: number) => {
  if (profit >= 20) {
    return { 
      bg: 'bg-emerald-500/20',  // Fond vert
      text: 'text-emerald-500',   // Texte vert
      label: 'Excellent' 
    };
  }
  if (profit >= 10) {
    return { 
      bg: 'bg-orange-500/20',     // Fond orange
      text: 'text-orange-500',    // Texte orange
      label: 'Bon' 
    };
  }
  return { 
    bg: 'bg-slate-600/20',        // Fond gris
    text: 'text-slate-400',       // Texte gris
    label: 'Standard' 
  };
};
```

**Visual** :
```
┌─────────────────────────────┐
│ Badge de profit (top-right) │
│                             │
│ +35.2%  (Vert/Excellent)   │
│ +15.8%  (Orange/Bon)       │
│ +5.3%   (Gris/Standard)    │
└─────────────────────────────┘
```

---

### 4. Rafraîchissement Manuel (FAB)

**Description** : Bouton flottant pour rafraîchir les données manuellement.

**Implémentation** :
```typescript
// RefreshButton.tsx
const handleRefresh = async () => {
  setIsLoading(true);
  const result = await refreshDeals();
  
  if (result.success) {
    setShowFeedback(true);
    window.location.reload(); // Hard refresh
  }
};
```

**Comportement** :
1. User clique le bouton
2. Spinner apparaît (loading state)
3. Server invalide les tags de cache
4. Page se recharge
5. Toast "✓ Données actualisées" s'affiche 2s

**Visual** :
```
FAB Position: bottom-6 right-3
┌─────────┐
│   ⟳    │ ← Icône RefreshCw
│ (spin)  │
└─────────┘
Hover: bg-emerald-400
Click: scale-90 animation
```

---

## 🎨 UI Components

### DealCard Component

**Props** :
```typescript
interface DealCardProps {
  deal: IDeal;
  onClick?: () => void;
}
```

**Features** :
- ✅ Image avec fallback SVG
- ✅ Badge profit coloré
- ✅ Badge source (Idealo/Leboncoin)
- ✅ Titre tronqué (45 chars)
- ✅ Catégorie + Localisation
- ✅ Pricing 2-colonnes
- ✅ Stock status
- ✅ Z-Score
- ✅ Hover state
- ✅ Tap feedback mobile

**Layout Responsive** :
```
Mobile (100% width):
┌─────────────────┐
│ Image (h-32)    │
├─────────────────┤
│ Badges overlay  │
├─────────────────┤
│ Title (2-lines) │
│ Category/Loc    │
├─────────────────┤
│ Sniper │ Ref    │
├─────────────────┤
│ Stock │ Score   │
└─────────────────┘
```

### CategoryFilter Component

**Features** :
- ✅ Sticky top (z-40)
- ✅ Horizontal scroll on mobile
- ✅ Active state highlight
- ✅ Smooth transitions
- ✅ Disabled state while loading

### DealList Component

**States** :
1. **Loading** : `DealListSkeleton` (6 placeholders)
2. **Error** : `AlertCircle` icon + error message
3. **Empty** : `TrendingDown` icon + message
4. **Success** : Stats header + DealCard list

**Stats Header** :
```
┌─────────────┬─────────────┬─────────────┐
│   42        │   +12.3%    │    +35%     │
│   Deals     │   Avg Profit│  Meilleur   │
└─────────────┴─────────────┴─────────────┘
```

### DealSkeleton Component

**Animation** : `animate-pulse` (Tailwind)

Crée un placeholder qui imite la structure de DealCard.

---

## 📊 Data Features

### Server Action: getDeals()

**Signature** :
```typescript
export async function getDeals(category?: string): Promise<DealsResponse>

interface DealsResponse {
  success: boolean;
  data?: IDeal[];
  error?: string;
  count?: number;
  timestamp?: Date;
}
```

**Query** :
```typescript
let query = {
  availability: { $ne: 'Out of Stock' },
};

if (category && category !== 'All') {
  query.category = category;
}

const deals = await Deal.find(query)
  .sort({ profit_margin: -1, z_score: -1 })
  .limit(100)
  .lean()
  .exec();
```

**Performance** :
- Indexes utilisés : O(log n)
- Max results : 100
- Average response time : 50-150ms

### Server Action: getDealById()

**Récupère un deal spécifique** :
```typescript
const response = await getDealById('507f1f77bcf86cd799439011');
```

**Utilisation** : Detail page (à implémenter)

### Server Action: getDealStats()

**Récupère les statistiques globales** :
```typescript
const stats = await getDealStats();

// Retourne:
{
  success: true,
  stats: {
    total: 42,
    avgProfitMargin: 12.5,
    bestDeal: {...},
    byCategory: {
      'Smartphones': 18,
      'Consoles': 15,
      'Laptops': 9
    }
  }
}
```

### Server Action: refreshDeals()

**Revalide le cache** :
```typescript
revalidateTag('deals-all');
revalidateTag('deals-Smartphones');
revalidateTag('deals-Consoles');
revalidateTag('deals-Laptops');
```

---

## 🤖 Telegram Integration

### TelegramProvider Context

**Expose** :
```typescript
interface TelegramContextType {
  user: TelegramUser | null;      // Utilisateur actuel
  isReady: boolean;               // SDK prêt
  webApp: typeof WebApp | null;   // WebApp object
  isMiniApp: boolean;             // Si on est dans Telegram
}
```

**Usage** :
```typescript
const { user, isReady } = useTelegram();

if (user) {
  console.log(`Hello ${user.first_name} (ID: ${user.id})`);
}
```

### Features

1. **User ID Retrieval** :
```typescript
const user = WebApp.initDataUnsafe?.user;
// {
//   id: 123456789,
//   is_bot: false,
//   first_name: "John",
//   last_name: "Doe",
//   username: "johndoe",
//   language_code: "en"
// }
```

2. **Full Screen Mode** :
```typescript
WebApp.expand();
```

3. **Header Color** :
```typescript
WebApp.setHeaderColor('secondary_bg_color');
```

4. **Safe Area Handling** :
```css
padding-left: env(safe-area-inset-left);
padding-right: env(safe-area-inset-right);
padding-bottom: env(safe-area-inset-bottom);
```

---

## 🚀 Future Features

### Phase 2 (À Implémenter)

#### 1. Détail Deal Page
```
Route: /deals/[dealId]
```
- Full product image gallery
- Description complète
- Historique des prix
- Lien d'achat direct

#### 2. Historique Utilisateur
```
Save viewed deals
Track purchase history
Personal analytics
```

#### 3. Notifications Push
```typescript
// Via Telegram API
WebApp.sendData(JSON.stringify({ 
  event: 'new_deal',
  deal_id: '...'
}))
```

#### 4. Filtres Avancés
```
- Price range slider
- Profit min/max
- Availability filter
- Source filter (Idealo vs Leboncoin)
- Location search
```

#### 5. Favoris / Watchlist
```typescript
interface FavoriteCard extends IDeal {
  user_id: number;
  added_at: Date;
  price_drop_alert?: number; // 5% = notify if price drops
}
```

#### 6. Partage Deal
```typescript
// Share button
const shareText = `
Superbe deal! 
${deal.title}
${deal.current_price}€ → Vendre ${deal.idealo_price}€
Profit: +${deal.profit_margin}%
${deal.url}
`;

// Share via Telegram
WebApp.sendData(shareText);
```

#### 7. Analytics
```typescript
// Track
- View count
- Click-through rate
- Average profit tracked
- Most viewed category
```

#### 8. API Rate Limiting
```typescript
// Prevent abuse
- Max 100 requests/hour per user
- Cache at user level
```

---

## 📋 Feature Checklist

**Complété** :
- ✅ Deal listing
- ✅ Category filtering
- ✅ Profit badge coloring
- ✅ Manual refresh
- ✅ Skeleton loading
- ✅ Telegram integration
- ✅ Responsive design
- ✅ Error handling

**À Faire** :
- ⏳ Deal detail page
- ⏳ User history
- ⏳ Push notifications
- ⏳ Advanced filters
- ⏳ Favorites/watchlist
- ⏳ Deal sharing
- ⏳ User analytics
- ⏳ Rate limiting

---

**Last Updated** : 21 mai 2026
**Status** : Core features complete, ready for Phase 2 development
