'use client';

import { useRouter, useSearchParams } from 'next/navigation';
import { RefreshCw, Search } from 'lucide-react';

export default function HorizontalFilterBar({ data }: { data: any[] }) {
  const router = useRouter();
  const searchParams = useSearchParams();

  // Filtrage intelligent pour réduire les options selon les sélections précédentes
  const getFilteredData = () => {
    let filtered = [...data];
    if (searchParams.get('category')) filtered = filtered.filter(d => d.category === searchParams.get('category'));
    if (searchParams.get('brand')) filtered = filtered.filter(d => d.brand === searchParams.get('brand'));
    return filtered;
  };

  const currentData = getFilteredData();

  const updateFilter = (key: string, value: string | null) => {
    const params = new URLSearchParams(searchParams.toString());
    if (!value || value === 'Tous') params.delete(key);
    else params.set(key, value);
    
    // Réinitialisation intelligente des dépendances
    if (key === 'category') { params.delete('brand'); params.delete('product_model'); }
    if (key === 'brand') params.delete('product_model');
    
    router.push(`/?${params.toString()}`);
  };

  const getOptions = (key: string) => {
    const values = Array.from(new Set(currentData.map((d) => d[key]).filter((v) => v))).sort();
    return ['Tous', ...values];
  };

  return (
    <div className="bg-slate-900/50 p-4 rounded-xl border border-slate-800 w-full space-y-4">
      {/* LIGNE 1 : Recherche + Catégories */}
      <div className="flex flex-row items-end gap-3 w-full">
        <div className="flex-[2]">
          <label className="text-[9px] font-bold text-slate-500 uppercase tracking-wider mb-1 block">Recherche</label>
          <div className="relative">
            <Search className="absolute left-2 top-2.5 text-slate-600" size={16} />
            <input
              type="text"
              placeholder="Ex: iPhone 15..."
              className="w-full bg-slate-950 text-white pl-8 p-2 rounded-lg border border-slate-800 text-xs focus:border-emerald-500 outline-none"
              defaultValue={searchParams.get('search') ?? ''}
              onKeyDown={(e) => e.key === 'Enter' && updateFilter('search', e.currentTarget.value)}
            />
          </div>
        </div>

        {['category', 'brand'].map((key) => (
          <div key={key} className="flex-1">
            <label className="text-[9px] font-bold text-slate-500 uppercase tracking-wider mb-1 block">
                {key === 'brand' ? 'Marque' : 'Catégorie'}
            </label>
            <select
              onChange={(e) => updateFilter(key, e.target.value)}
              value={searchParams.get(key) ?? 'Tous'}
              className="w-full bg-slate-950 text-white p-2 rounded-lg border border-slate-800 text-xs focus:border-emerald-500 outline-none"
            >
              {getOptions(key).map((val) => <option key={val} value={val}>{val}</option>)}
            </select>
          </div>
        ))}
      </div>

      {/* LIGNE 2 : Modèle + Prix */}
      <div className="flex flex-row items-end gap-3 w-full">
        <div className="flex-[2]">
          <label className="text-[9px] font-bold text-slate-500 uppercase tracking-wider mb-1 block">Modèle</label>
          <select
            onChange={(e) => updateFilter('product_model', e.target.value)}
            value={searchParams.get('product_model') ?? 'Tous'}
            className="w-full bg-slate-950 text-white p-2 rounded-lg border border-slate-800 text-xs focus:border-emerald-500 outline-none"
          >
            {getOptions('product_model').map((val) => <option key={val} value={val}>{val}</option>)}
          </select>
        </div>
        
        <div className="flex-1">
          <label className="text-[9px] font-bold text-slate-500 uppercase tracking-wider mb-1 block">Min (€)</label>
          <input type="number" placeholder="0" className="w-full bg-slate-950 text-white p-2 rounded-lg border border-slate-800 text-xs" 
                 defaultValue={searchParams.get('minPrice') ?? ''}
                 onBlur={(e) => updateFilter('minPrice', e.target.value)} />
        </div>
        <div className="flex-1">
          <label className="text-[9px] font-bold text-slate-500 uppercase tracking-wider mb-1 block">Max (€)</label>
          <input type="number" placeholder="Max" className="w-full bg-slate-950 text-white p-2 rounded-lg border border-slate-800 text-xs" 
                 defaultValue={searchParams.get('maxPrice') ?? ''}
                 onBlur={(e) => updateFilter('maxPrice', e.target.value)} />
        </div>
        
        <button onClick={() => router.push('/')} className="p-2.5 bg-slate-800 hover:bg-slate-700 text-slate-400 rounded-lg transition-all">
          <RefreshCw size={16} />
        </button>
      </div>
    </div>
  );
}