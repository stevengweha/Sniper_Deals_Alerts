import { getDashboardData } from '@/lib/data';
import HorizontalFilterBar from '@/components/CategoryFilter';
import { DealList } from '@/components/DealList';
import { BestDeal } from '@/components/BestDeal';

export default async function Dashboard({ searchParams }: { searchParams: Record<string, string | string[] | undefined> }) {
  const filters = {
    category: typeof searchParams.category === 'string' ? searchParams.category : undefined,
    brand: typeof searchParams.brand === 'string' ? searchParams.brand : undefined,
    product_model: typeof searchParams.product_model === 'string' ? searchParams.product_model : undefined,
    source: typeof searchParams.source === 'string' ? searchParams.source : undefined,
    product_condition: typeof searchParams.product_condition === 'string' ? searchParams.product_condition : undefined,
    minPrice: typeof searchParams.minPrice === 'string' ? parseInt(searchParams.minPrice) : undefined,
    maxPrice: typeof searchParams.maxPrice === 'string' ? parseInt(searchParams.maxPrice) : undefined,
    search: typeof searchParams.search === 'string' ? searchParams.search : undefined,
  };

  const rawData = await getDashboardData(filters);
  const deals = rawData?.deals || [];
  const allDeals = rawData?.allDeals || [];
  const stats = rawData?.stats || { 
    totalDeals: 0, avgPrice: 0, bestPrice: 0, avgProfit: 0, 
    bestProfit: 0, totalPotentialProfit: 0, bestSource: 'N/A' 
  };

  return (
    <main className="min-h-screen bg-[#020617] p-4 md:p-8">
      <div className="max-w-7xl mx-auto space-y-8">
        
        {/* HEADER */}
        <header>
          <h1 className="text-4xl font-black text-white tracking-tight">Smart Buy <span className="text-emerald-500">Sentinel</span></h1>
          <p className="text-slate-400 mt-1">Intelligence de marché • {stats.totalDeals} opportunités actives</p>
        </header>

        {/* FILTRES PLEINE LARGEUR */}
        <section className="w-full">
          <HorizontalFilterBar data={allDeals} />
        </section>

        {/* SECTION STATS */}
        <section className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <KpiCard label="Offres Actives" value={stats.totalDeals.toString()} />
          <KpiCard label="Prix Moyen" value={`${stats.avgPrice.toFixed(0)}€`} />
          <KpiCard label="Meilleur Prix" value={`${stats.bestPrice}€`} accent="emerald" />
          <KpiCard label="Profit Moyen" value={`+${stats.avgProfit.toFixed(0)}€`} accent="green" />
        </section>

        <BestDeal deals={deals} />

        <section>
          <h2 className="text-xl font-bold text-white mb-6">📊 Flux d'opportunités</h2>
          <DealList deals={deals} />
        </section>
      </div>
    </main>
  );
}

function KpiCard({ label, value, accent = "white" }: { label: string, value: string, accent?: string }) {
  const colors: Record<string, string> = {
    white: "text-white",
    emerald: "text-emerald-400",
    green: "text-green-400"
  };
  return (
    <div className="bg-slate-900/50 backdrop-blur border border-slate-800 rounded-2xl p-5 hover:border-slate-700 transition-all">
      <p className="text-[10px] font-bold text-slate-500 uppercase tracking-widest mb-1">{label}</p>
      <p className={`text-2xl font-black ${colors[accent]}`}>{value}</p>
    </div>
  );
}