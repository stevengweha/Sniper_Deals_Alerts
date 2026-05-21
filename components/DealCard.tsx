'use client';

import React from 'react';
import { IDeal } from '@/models/Deal';

export const DealCard: React.FC<{ deal: IDeal }> = ({ deal }) => {
  const handleOpen = () => {
    if (typeof window !== 'undefined' && (window as any).Telegram?.WebApp) {
      const tg = (window as any).Telegram.WebApp;
      tg.HapticFeedback.impactOccurred('light');
      tg.openLink(deal.url);
    } else {
      window.open(deal.url, '_blank');
    }
  };

  const profitColor = deal.estimated_resell_profit && deal.estimated_resell_profit > 300 ? 'text-green-400' : deal.estimated_resell_profit && deal.estimated_resell_profit > 100 ? 'text-yellow-400' : 'text-red-400';
  const dealBadgeColor = deal.deal_score?.includes('EXCELLENT') ? 'bg-emerald-900' : deal.deal_score?.includes('TRÈS') ? 'bg-blue-900' : 'bg-slate-800';

  return (
    <button
      onClick={handleOpen}
      className="w-full text-left bg-slate-900 border border-slate-800 rounded-lg p-4 hover:border-emerald-500/50 transition-all active:scale-[0.98]"
    >
      {/* En-tête : badge + profit */}
      <div className="flex justify-between items-start mb-2 gap-2">
        <span className={`text-xs font-bold px-2 py-1 rounded ${dealBadgeColor} text-white`}>
          {deal.category}
        </span>
        <span className={`font-bold text-sm ${profitColor}`}>
          +{deal.estimated_resell_profit?.toFixed(0) || 0}€
        </span>
      </div>

      {/* Deal Score (pour context) */}
      {deal.deal_score && (
        <p className="text-xs text-slate-400 mb-2">{deal.deal_score}</p>
      )}

      {/* Titre du produit */}
      <h3 className="font-semibold text-sm text-slate-100 line-clamp-2 mb-3">
        {deal.title}
      </h3>

      {/* Grille d'infos */}
      <div className="grid grid-cols-2 gap-2 text-xs border-t border-slate-800 pt-2">
        <div>
          <span className="text-slate-500">Prix:</span>
          <span className="text-white font-bold ml-1">{deal.price}€</span>
        </div>
        <div>
          <span className="text-slate-500">Médiane:</span>
          <span className="text-slate-300 font-bold ml-1">{deal.median_model_price?.toFixed(0) || '—'}€</span>
        </div>
        <div>
          <span className="text-slate-500">Écart:</span>
          <span className={`font-bold ml-1 ${deal.pct_deviation && deal.pct_deviation < -20 ? 'text-green-400' : 'text-red-400'}`}>
            {deal.pct_deviation?.toFixed(1) || '—'}%
          </span>
        </div>
        <div>
          <span className="text-slate-500">Données:</span>
          <span className="text-slate-300 font-bold ml-1">{deal.data_age_hours || '—'}h</span>
        </div>
      </div>

      {/* Modèle + Source */}
      <div className="flex justify-between gap-2 mt-2 pt-2 border-t border-slate-700 text-xs">
        <span className="text-slate-400">{deal.product_model}</span>
        <span className="text-slate-500 font-semibold uppercase">{deal.source}</span>
      </div>
    </button>
  );
};