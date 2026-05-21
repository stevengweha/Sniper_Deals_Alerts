import { getDashboardData } from '@/lib/data';
import FilterSidebar from '@/components/CategoryFilter';
import { DealList } from '@/components/DealList';
import { BestDeal } from '@/components/BestDeal';
import { TopDeals } from '@/components/TopDeals';

export default async function Dashboard({ searchParams }: { searchParams: Record<string, string | string[] | undefined> }) {
  // 1. Normalisation des filtres
  const filters = {
    category: typeof searchParams.category === 'string' ? searchParams.category : undefined,
    brand: typeof searchParams.brand === 'string' ? searchParams.brand : undefined,
    product_model: typeof searchParams.product_model === 'string' ? searchParams.product_model : undefined,
    storage_capacity: typeof searchParams.storage_capacity === 'string' ? searchParams.storage_capacity : undefined,
    source: typeof searchParams.source === 'string' ? searchParams.source : undefined,
    product_condition: typeof searchParams.product_condition === 'string' ? searchParams.product_condition : undefined,
    minPrice: typeof searchParams.minPrice === 'string' ? parseInt(searchParams.minPrice) : undefined,
    maxPrice: typeof searchParams.maxPrice === 'string' ? parseInt(searchParams.maxPrice) : undefined,
    search: typeof searchParams.search === 'string' ? searchParams.search : undefined,
  };

  // 2. Récupération des données (Parallélisation)
  const [allDeals, filteredDeals] = await Promise.all([
    getDashboardData(),
    getDashboardData(filters)
  ]);

  // 3. Calculs des KPIs
  const totalDeals = filteredDeals.length;
  const avgPrice = totalDeals > 0 ? filteredDeals.reduce((sum: number, d: any) => sum + (d.price || 0), 0) / totalDeals : 0;
  const avgProfit = totalDeals > 0 ? filteredDeals.reduce((sum: number, d: any) => sum + (d.estimated_resell_profit || 0), 0) / totalDeals : 0;
  const bestProfit = totalDeals > 0 ? Math.max(...filteredDeals.map((d: any) => d.estimated_resell_profit || 0)) : 0;
  const bestPrice = totalDeals > 0 ? Math.min(...filteredDeals.map((d: any) => d.price || Infinity)) : 0;
  const totalPotentialProfit = filteredDeals.reduce((sum: number, d: any) => sum + Math.max(0, d.estimated_resell_profit || 0), 0);

  const dealsBySource = filteredDeals.reduce((acc: Record<string, number>, d: any) => {
    acc[d.source || 'Inconnu'] = (acc[d.source || 'Inconnu'] || 0) + 1;
    return acc;
  }, {});
  const bestSource = Object.entries(dealsBySource).sort(([, a], [, b]) => (b as number) - (a as number))[0]?.[0] || 'N/A';

  return (
    <main className="min-h-screen bg-slate-950 p-4 md:p-6 flex flex-col md:flex-row gap-6">
      {/* SIDEBAR */}
      <aside className="w-full md:w-72 shrink-0">
        <FilterSidebar data={allDeals} />
      </aside>

      {/* CONTENU PRINCIPAL */}
      <section className="flex-1 space-y-8">
        
        {/* HEADER */}
        <div>
          <h1 className="text-3xl font-bold text-white mb-2">📡 Smart Buy Sentinel</h1>
          <p className="text-slate-400 text-sm">Intelligence de marché temps-réel — <strong>{totalDeals}</strong> offres filtrées</p>
        </div>

        {/* KPIS */}
        <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
          <KpiCard label="Nombre d'offres" value={totalDeals.toString()} />
          <KpiCard label="Prix moyen" value={`${avgPrice.toFixed(0)}€`} />
          <KpiCard label="Meilleur prix" value={`${bestPrice === Infinity ? 0 : bestPrice}€`} color="emerald" />
          <KpiCard label="Profit moyen" value={`+${avgProfit.toFixed(0)}€`} color="green" />
        </div>

        {/* HIGHLIGHTS */}
        {totalDeals > 0 && (
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <BestDeal deals={filteredDeals} />
            <TopDeals deals={filteredDeals} />
          </div>
        )}

        {/* STATS SECONDAIRES */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <StatBox label="Meilleur profit" value={`+${bestProfit.toFixed(0)}€`} color="green" />
          <StatBox label="Profit total potentiel" value={`+${totalPotentialProfit.toFixed(0)}€`} color="emerald" />
          <StatBox label="Meilleure source" value={bestSource} color="yellow" />
        </div>

        {/* LISTE */}
        <DealList deals={filteredDeals} />
      </section>
    </main>
  );
}

// Composants utilitaires pour alléger le code
function KpiCard({ label, value, color = "white" }: { label: string, value: string, color?: string }) {
  return (
    <div className="bg-slate-900 border border-slate-800 rounded-xl p-4">
      <p className="text-slate-500 text-[10px] font-bold uppercase tracking-wider mb-1">{label}</p>
      <p className={`text-${color}-400 text-2xl font-bold`}>{value}</p>
    </div>
  );
}

function StatBox({ label, value, color }: { label: string, value: string, color: string }) {
  return (
    <div className="bg-slate-900 border border-slate-800 rounded-xl p-4">
      <p className="text-slate-500 text-xs font-bold uppercase mb-2">{label}</p>
      <p className={`text-${color}-400 text-xl font-bold`}>{value}</p>
    </div>
  );
}