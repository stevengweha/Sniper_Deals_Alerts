'use client';

import { IDeal } from '@/models/Deal';

export const TopDeals = ({ deals }: { deals: IDeal[] }) => {
  if (!deals || deals.length === 0) {
    return null;
  }

  const topDeals = [...deals]
    .sort((a, b) => (b.estimated_resell_profit || 0) - (a.estimated_resell_profit || 0))
    .slice(0, 10);

  if (topDeals.length === 0) {
    return null;
  }

  return (
    <div>
      <h2 className="text-xl font-bold text-white mb-4 flex items-center gap-2">
        💎 Top 10 des Meilleures Marges
      </h2>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-5 gap-3">
        {topDeals.map((deal) => {
          const profitColor =
            (deal.estimated_resell_profit || 0) > 300
              ? 'bg-emerald-900 text-emerald-100'
              : (deal.estimated_resell_profit || 0) > 100
              ? 'bg-blue-900 text-blue-100'
              : 'bg-slate-800 text-slate-100';

          return (
            <button
              key={String(deal._id)}
              onClick={() => {
                if (typeof window !== 'undefined' && (window as any).Telegram?.WebApp) {
                  const tg = (window as any).Telegram.WebApp;
                  tg.openLink(deal.url);
                } else {
                  window.open(deal.url, '_blank');
                }
              }}
              className={`rounded-lg p-3 border border-slate-700 hover:border-emerald-500 transition-all text-left ${profitColor} group`}
            >
              {/* Source badge */}
              <div className="text-xs font-bold uppercase text-slate-400 mb-1">
                {deal.source}
              </div>

              {/* Modèle */}
              <p className="text-xs text-slate-300 mb-1 line-clamp-1">{deal.product_model}</p>

              {/* Capacité */}
              <p className="text-xs text-slate-400 mb-2">{deal.storage_capacity}</p>

              {/* Titre */}
              <p className="text-xs font-semibold mb-2 line-clamp-2 h-8">
                {String(deal.title).substring(0, 40)}
              </p>

              {/* Prix */}
              <div className="text-lg font-bold mb-1">{deal.price?.toFixed(0)}€</div>

              {/* Gain */}
              <div
                className={`text-sm font-bold mb-2 ${
                  (deal.estimated_resell_profit || 0) > 0 ? 'text-green-400' : 'text-red-400'
                }`}
              >
                Gain: +{deal.estimated_resell_profit?.toFixed(0) || 0}€
              </div>

              {/* Lien */}
              <div className="text-xs font-semibold text-emerald-400 opacity-0 group-hover:opacity-100 transition-opacity">
                Voir l'offre →
              </div>
            </button>
          );
        })}
      </div>
    </div>
  );
};
