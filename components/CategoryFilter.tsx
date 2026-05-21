'use client';

import { useRouter, useSearchParams } from 'next/navigation';
import { useCallback } from 'react';

export default function FilterSidebar({ data }: { data: any[] }) {
  const router = useRouter();
  const searchParams = useSearchParams();

  const updateFilter = useCallback(
    (key: string, value: string | null) => {
      const params = new URLSearchParams(searchParams.toString());
      if (value === null || value === 'Tous' || value === 'Toutes' || value === 'All') {
        params.delete(key);
      } else {
        params.set(key, value);
      }
      router.push(`/?${params.toString()}`);
    },
    [searchParams, router]
  );

  const getUnique = (key: string) => {
    const values = Array.from(
      new Set(
        data
          .map((d) => d[key])
          .filter((v) => v != null && String(v).trim() !== '')
      )
    ).sort();
    return ['Tous', ...values];
  };

  // Calcul dynamique des prix
  const allPrices = data
    .map((d) => d.price)
    .filter((p) => typeof p === 'number')
    .sort((a, b) => a - b);
  const minPriceAvailable = allPrices[0] ?? 0;
  const maxPriceAvailable = allPrices[allPrices.length - 1] ?? 1000;

  return (
    <div className="w-full md:w-72 bg-slate-900 p-4 rounded-xl h-fit border border-slate-800 sticky top-4">
      <h2 className="text-white font-bold mb-4 flex items-center gap-2">
        🎯 Options du Radar
      </h2>

      <div className="space-y-4">
        {/* Catégorie */}
        <div>
          <label className="text-slate-400 text-xs font-bold uppercase block mb-2">
            📂 Catégorie
          </label>
          <select
            onChange={(e) => updateFilter('category', e.target.value === 'Tous' ? null : e.target.value)}
            defaultValue={searchParams.get('category') ?? 'Tous'}
            className="w-full bg-slate-950 text-white p-2 rounded border border-slate-700 text-sm"
          >
            {getUnique('category').map((c) => (
              <option key={c} value={c}>
                {c}
              </option>
            ))}
          </select>
        </div>

        {/* Marque */}
        <div>
          <label className="text-slate-400 text-xs font-bold uppercase block mb-2">
            🏷️ Marque
          </label>
          <select
            onChange={(e) => updateFilter('brand', e.target.value === 'Tous' ? null : e.target.value)}
            defaultValue={searchParams.get('brand') ?? 'Tous'}
            className="w-full bg-slate-950 text-white p-2 rounded border border-slate-700 text-sm"
          >
            {getUnique('brand').map((b) => (
              <option key={b} value={b}>
                {b}
              </option>
            ))}
          </select>
        </div>

        {/* Modèle */}
        <div>
          <label className="text-slate-400 text-xs font-bold uppercase block mb-2">
            📱 Modèle
          </label>
          <select
            onChange={(e) => updateFilter('product_model', e.target.value === 'Tous' ? null : e.target.value)}
            defaultValue={searchParams.get('product_model') ?? 'Tous'}
            className="w-full bg-slate-950 text-white p-2 rounded border border-slate-700 text-sm"
          >
            {getUnique('product_model').map((m) => (
              <option key={m} value={m}>
                {m}
              </option>
            ))}
          </select>
        </div>

        {/* État du produit */}
        <div>
          <label className="text-slate-400 text-xs font-bold uppercase block mb-2">
            🛡️ État
          </label>
          <select
            onChange={(e) => updateFilter('product_condition', e.target.value === 'Tous' ? null : e.target.value)}
            defaultValue={searchParams.get('product_condition') ?? 'Tous'}
            className="w-full bg-slate-950 text-white p-2 rounded border border-slate-700 text-sm"
          >
            {getUnique('product_condition').map((c) => (
              <option key={c} value={c}>
                {c}
              </option>
            ))}
          </select>
        </div>

        {/* Source */}
        <div>
          <label className="text-slate-400 text-xs font-bold uppercase block mb-2">
            🛒 Source
          </label>
          <select
            onChange={(e) => updateFilter('source', e.target.value === 'Tous' ? null : e.target.value)}
            defaultValue={searchParams.get('source') ?? 'Tous'}
            className="w-full bg-slate-950 text-white p-2 rounded border border-slate-700 text-sm"
          >
            {getUnique('source').map((s) => (
              <option key={s} value={s}>
                {s}
              </option>
            ))}
          </select>
        </div>

        {/* Prix */}
        <div>
          <label className="text-slate-400 text-xs font-bold uppercase block mb-2">
            💰 Prix (€)
          </label>
          <div className="flex gap-2">
            <input
              type="number"
              placeholder="Min"
              defaultValue={searchParams.get('minPrice') ?? minPriceAvailable}
              onChange={(e) => updateFilter('minPrice', e.target.value || null)}
              className="w-1/2 bg-slate-950 text-white p-2 rounded border border-slate-700 text-sm"
            />
            <input
              type="number"
              placeholder="Max"
              defaultValue={searchParams.get('maxPrice') ?? maxPriceAvailable}
              onChange={(e) => updateFilter('maxPrice', e.target.value || null)}
              className="w-1/2 bg-slate-950 text-white p-2 rounded border border-slate-700 text-sm"
            />
          </div>
        </div>

        {/* Recherche */}
        <div>
          <label className="text-slate-400 text-xs font-bold uppercase block mb-2">
            🔍 Recherche
          </label>
          <input
            type="text"
            placeholder="Mot-clé..."
            defaultValue={searchParams.get('search') ?? ''}
            onChange={(e) => updateFilter('search', e.target.value || null)}
            className="w-full bg-slate-950 text-white p-2 rounded border border-slate-700 text-sm"
          />
        </div>
      </div>
    </div>
  );
}
