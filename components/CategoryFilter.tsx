'use client';

import { useRouter, useSearchParams } from 'next/navigation';
import { RefreshCw, Search } from 'lucide-react';

// Typage strict pour éviter les erreurs
export type FilterOptions = {
  categories: string[];
  brands: string[];
  models: string[];
};

export default function HorizontalFilterBar({ options }: { options: FilterOptions }) {
  const router = useRouter();
  const searchParams = useSearchParams();

  const updateFilter = (key: string, value: string | null) => {
    const params = new URLSearchParams(searchParams.toString());
    if (!value || value === 'Tous') params.delete(key);
    else params.set(key, value);
    
    // Réinitialisation en cascade
    if (key === 'category') { params.delete('brand'); params.delete('product_model'); }
    if (key === 'brand') params.delete('product_model');
    
    router.push(`/?${params.toString()}`);
    // Astuce mobile : retire le focus pour fermer le clavier
    (document.activeElement as HTMLElement)?.blur();
  };

  // STYLE CORRECTION : font-size: 16px empêche le zoom auto sur iOS
  const inputClass = "w-full bg-slate-950 text-white p-3 rounded-lg border border-slate-800 text-[16px] focus:border-emerald-500 outline-none";

  return (
    <div className="bg-slate-900/50 p-4 rounded-xl border border-slate-800 w-full space-y-4">
      <div className="flex flex-row items-end gap-3 w-full">
        <div className="flex-[2]">
          <label className="text-[10px] font-bold text-slate-500 uppercase tracking-wider mb-1 block">Recherche</label>
          <div className="relative">
            <Search className="absolute left-3 top-3.5 text-slate-600" size={18} />
            <input
              type="text"
              placeholder="Ex: iPhone 15..."
              className={`${inputClass} pl-10`}
              defaultValue={searchParams.get('search') ?? ''}
              onKeyDown={(e) => e.key === 'Enter' && updateFilter('search', e.currentTarget.value)}
            />
          </div>
        </div>

        <div className="flex-1">
          <label className="text-[10px] font-bold text-slate-500 uppercase tracking-wider mb-1 block">Catégorie</label>
          <select
            onChange={(e) => updateFilter('category', e.target.value)}
            value={searchParams.get('category') ?? 'Tous'}
            className={inputClass}
          >
            <option value="Tous">Tous</option>
            {options.categories.map((val) => <option key={val} value={val}>{val}</option>)}
          </select>
        </div>

        <div className="flex-1">
          <label className="text-[10px] font-bold text-slate-500 uppercase tracking-wider mb-1 block">Marque</label>
          <select
            onChange={(e) => updateFilter('brand', e.target.value)}
            value={searchParams.get('brand') ?? 'Tous'}
            className={inputClass}
          >
            <option value="Tous">Tous</option>
            {options.brands.map((val) => <option key={val} value={val}>{val}</option>)}
          </select>
        </div>
      </div>

      <div className="flex flex-row items-end gap-3 w-full">
        <div className="flex-[2]">
          <label className="text-[10px] font-bold text-slate-500 uppercase tracking-wider mb-1 block">Modèle</label>
          <select
            onChange={(e) => updateFilter('product_model', e.target.value)}
            value={searchParams.get('product_model') ?? 'Tous'}
            className={inputClass}
          >
            <option value="Tous">Tous</option>
            {options.models.map((val) => <option key={val} value={val}>{val}</option>)}
          </select>
        </div>
        
        <div className="flex-1">
          <label className="text-[10px] font-bold text-slate-500 uppercase tracking-wider mb-1 block">Min (€)</label>
          <input type="number" placeholder="0" className={inputClass} 
                 defaultValue={searchParams.get('minPrice') ?? ''}
                 onBlur={(e) => updateFilter('minPrice', e.target.value)} />
        </div>
        <div className="flex-1">
          <label className="text-[10px] font-bold text-slate-500 uppercase tracking-wider mb-1 block">Max (€)</label>
          <input type="number" placeholder="Max" className={inputClass} 
                 defaultValue={searchParams.get('maxPrice') ?? ''}
                 onBlur={(e) => updateFilter('maxPrice', e.target.value)} />
        </div>
        
        <button onClick={() => router.push('/')} className="p-3.5 bg-slate-800 hover:bg-slate-700 text-slate-400 rounded-lg transition-all">
          <RefreshCw size={18} />
        </button>
      </div>
    </div>
  );
}