# TODO - Adapter l’app Next.js à tes tables Mongo (streamlit simplifié)

## Étape 1 — Comprendre le modèle actuel (fait)
- [x] Lire `app/page.tsx`
- [x] Lire `actions/deals.ts`
- [x] Lire `components/DealCard.tsx`
- [x] Lire `components/DealList.tsx`
- [x] Lire `models/Deal.ts`

## Étape 2 — Mettre à jour le schéma & types Mongo
- [x] Modifier `models/Deal.ts` pour correspondre à: `price`, `avg_model_price`, `median_model_price`, `pct_deviation`, `estimated_resell_profit`, `deal_score`, `operational_status`, `product_model`, `brand`, `category`, `screen_size`, `storage_capacity`, `data_age_hours`, `model_price_volatility`, `model_volume`, `z_score`, `product_condition`, `source`, `url`, `product_id`, `timestamp`.


## Étape 3 — Adapter les Server Actions
- [x] Mettre à jour `actions/deals.ts`:
  - [x] Query `operational_status === "🟢 Actif"`
  - [x] Filtrer par `category`
  - [x] Trier par `estimated_resell_profit` DESC puis `z_score`
  - [x] Recalculer `getDealStats()` (KPIs)

## Étape 4 — Réécrire le dashboard UI simplifié
- [ ] Modifier `app/page.tsx` pour afficher seulement la catégorie filtrée + KPIs
- [ ] Modifier `components/DealCard.tsx` pour:
  - [ ] badge basé sur `deal_score` / `estimated_resell_profit`
  - [ ] afficher `price`, `median_model_price`, `pct_deviation`, `estimated_resell_profit`, `data_age_hours`, `product_condition`, `source`
  - [ ] bouton ouvre `url`
- [ ] Modifier `components/DealList.tsx` pour afficher les listes + stats simplifiées.

## Étape 5 — Ajuster le filtre catégorie
- [ ] Modifier `components/CategoryFilter.tsx` si nécessaire (catégories attendues: `ORDINATEUR`, `SMARTPHONE`, etc.)


## Étape 6 — QA rapide
- [ ] `npm run type-check`
- [ ] `npm run dev` et vérifier:
  - [ ] Chargement deals
  - [ ] Tri et filtres
  - [ ] Rendu card
  - [ ] Lien direct

