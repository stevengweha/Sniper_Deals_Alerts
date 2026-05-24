'use client';

import React, { useMemo } from 'react';
import { IDeal } from '@/models/Deal';

export const BestDeal = ({ deals }: { deals: IDeal[] }) => {
  // 1. Optimisation : on utilise useMemo pour trier uniquement si 'deals' change
  const bestDeal = useMemo(() => {
    if (!deals || deals.length === 0) return null;
    return [...deals].sort((a, b) => (b.estimated_resell_profit || 0) - (a.estimated_resell_profit || 0))[0];
  }, [deals]);

  if (!bestDeal || (bestDeal.estimated_resell_profit || 0) <= 0) return null;

  const handleOpen = () => {
    const tg = typeof window !== 'undefined' ? (window as any).Telegram?.WebApp : null;
    if (tg) {
      tg.HapticFeedback.impactOccurred('light');
      tg.openLink(bestDeal.url);
    } else {
      window.open(bestDeal.url, '_blank');
    }
  };

  return (
    <div className="mb-8 bg-gradient-to-br from-slate-900 to-slate-950 border border-emerald-500/30 rounded-xl p-6 shadow-2xl">
      <h2 className="text-sm font-bold text-emerald-400 mb-6 flex items-center gap-2 uppercase tracking-widest">
        <span className="animate-pulse">⚡</span> Opportunité Or à Saisir
      </h2>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-8 items-center">
        
        {/* JAUGE DE PROFIT */}
        <div className="flex justify-center">
          <div className="relative w-32 h-32 flex items-center justify-center">
            <div className="absolute inset-0 rounded-full border-4 border-slate-800"></div>
            <div className="text-center">
              <div className="text-2xl font-black text-white">
                +{bestDeal.estimated_resell_profit?.toFixed(0)}€
              </div>
              <div className="text-[10px] text-slate-500 uppercase">Profit Est.</div>
            </div>
          </div>
        </div>

        {/* INFOS PRODUIT */}
        <div className="space-y-3">
          <span className="text-[10px] font-bold bg-emerald-900/50 text-emerald-300 px-2 py-0.5 rounded border border-emerald-500/20">
            {bestDeal.deal_score || 'BEST MATCH'}
          </span>
          <h3 className="text-md font-bold text-white leading-tight">{bestDeal.title}</h3>
          
          <div className="grid grid-cols-2 gap-2 text-xs">
            <InfoRow label="Prix" value={`${bestDeal.price?.toFixed(0) || 0}€`} />
            <InfoRow label="Médiane" value={`${bestDeal.median_model_price?.toFixed(0) || 0}€`} />
            <InfoRow label="État" value={bestDeal.product_condition || 'N/A'} />
            <InfoRow label="Source" value={bestDeal.source || 'N/A'} />
          </div>
        </div>

        {/* ACTIONS */}
        <div className="flex flex-col gap-3">
          <div className="bg-slate-800/50 rounded-lg p-3 text-center border border-slate-700">
            <p className="text-[10px] text-slate-400 uppercase">Z-Score</p>
            <p className="text-emerald-400 font-mono font-bold text-lg">{bestDeal.z_score?.toFixed(2) || '0.00'}</p>
          </div>
          <button
            onClick={handleOpen}
            className="w-full bg-emerald-500 hover:bg-emerald-400 text-slate-950 font-black py-3 rounded-lg transition-all active:scale-95 shadow-[0_0_15px_rgba(16,185,129,0.3)]"
          >
            VOIR L'OFFRE 🚀
          </button>
        </div>
      </div>
    </div>
  );
};

const InfoRow = ({ label, value }: { label: string; value: string }) => (
  <div className="flex justify-between border-b border-slate-800 pb-1">
    <span className="text-slate-500">{label}</span>
    <span className="text-slate-200 font-medium">{value}</span>
  </div>
);