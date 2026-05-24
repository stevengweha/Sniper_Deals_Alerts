'use client';

import React, { memo } from 'react';
import { IDeal } from '@/models/Deal';
import { TrendingDown, ShieldCheck, Zap, Tag } from 'lucide-react';

export const DealCard = memo(({ deal }: { deal: IDeal }) => {
 
  const handleOpen = () => {
    if (typeof window !== 'undefined') {
      const tg = (window as any).Telegram?.WebApp;
      tg?.HapticFeedback?.impactOccurred('medium');
      tg ? tg.openLink(deal.url) : window.open(deal.url, '_blank');
    }
  };

  const isHighConf = deal.statistical_confidence?.includes('🟢');
  const scoreBadge = deal.deal_score?.split(' ')[0] || 'DEAL';

  return (
    <button
      onClick={handleOpen}
      className="w-full group text-left bg-slate-900/50 border border-slate-800 rounded-2xl p-5 hover:border-emerald-500/50 transition-all active:scale-[0.98] shadow-xl"
    >
      {/* Header : Score, Source et PRIX ACTUEL */}
      <div className="flex justify-between items-start mb-4">
        <div className="flex flex-col gap-2">
          <span className="flex items-center gap-1.5 text-[10px] font-bold text-emerald-400 uppercase tracking-widest bg-emerald-950/30 px-2 py-1 rounded-full border border-emerald-900/50 w-fit">
            <Zap size={10} /> {scoreBadge}
          </span>
        </div>
        <div className="text-right">
          <span className="text-[10px] text-slate-500 font-mono uppercase block">{deal.source}</span>
          {/* PRIX DE L'ARTICLE AJOUTÉ ICI */}
          <span className="text-xl font-black text-white">{deal.price ? `${deal.price.toFixed(0)}€` : 'N/A'}</span>
        </div>
      </div>

      {/* Titre */}
      <h3 className="font-bold text-white text-sm leading-snug group-hover:text-emerald-400 transition-colors mb-4 line-clamp-2">
        {deal.title}
      </h3>

      {/* Analyse de prix */}
      <div className="bg-slate-950/50 rounded-xl p-3 mb-4 border border-slate-800/50">
        <div className="flex justify-between items-center mb-2">
          <span className="text-[10px] text-slate-400 uppercase">Prix marché</span>
          <span className="text-slate-300 font-medium">{deal.median_model_price?.toFixed(0) || 0}€</span>
        </div>
        <div className="flex justify-between items-center">
          <span className="text-[10px] text-emerald-500 font-bold uppercase flex items-center gap-1">
            <TrendingDown size={12} /> Réduction
          </span>
          <span className="text-emerald-400 font-black">{deal.pct_deviation?.toFixed(0) || 0}%</span>
        </div>
      </div>

      {/* Footer : Gain et Confiance */}
      <div className="flex items-center justify-between border-t border-slate-800 pt-4">
        <div className="flex flex-col">
          <span className="text-[9px] text-slate-500 uppercase font-bold">Profit estimé</span>
          <span className="text-lg font-black text-emerald-400">+{deal.estimated_resell_profit?.toFixed(0) || 0}€</span>
        </div>
        
        <div className={`flex items-center gap-1 text-[10px] px-2 py-1 rounded ${isHighConf ? 'text-emerald-400' : 'text-yellow-500'}`}>
           <ShieldCheck size={12} />
           {isHighConf ? 'Confiance Liquide' : 'Volume Modéré'}
        </div>
      </div>
    </button>
  );
});

DealCard.displayName = 'DealCard';