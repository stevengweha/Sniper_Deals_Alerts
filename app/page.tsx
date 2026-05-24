import { getDashboardData } from '@/lib/data';
import HorizontalFilterBar from '@/components/CategoryFilter';
import { DealList } from '@/components/DealList';
import { BestDeal } from '@/components/BestDeal';
import Link from 'next/link';
import { ChevronLeft, ChevronRight } from 'lucide-react';

export default async function Dashboard({ searchParams }: { searchParams: Record<string, string | string[] | undefined> }) {
  // 1. Extraction propre des filtres
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

  // 2. Gestion de la page actuelle
  const currentPage = typeof searchParams.page === 'string' ? parseInt(searchParams.page) : 1;

  // 3. Appel des données
  const data = await getDashboardData(filters, currentPage);
  
  // 4. Sécurisation stricte des variables
  const deals = data?.deals || [];
  const filterOptions = data?.filterOptions || { categories: [], brands: [], models: [] };
  const stats = data?.stats || { avgPrice: 0, bestPrice: 0, avgProfit: 0, bestProfit: 0 };
  const pagination = data?.pagination || { totalDeals: 0, currentPage: 1, totalPages: 1 };

  // 5. Fonction utilitaire pour générer les liens de pagination en gardant les filtres
  const createPageURL = (pageNumber: number) => {
    const params = new URLSearchParams();
    Object.entries(searchParams).forEach(([key, value]) => {
      if (value && key !== 'page') {
        params.set(key, String(value));
      }
    });
    params.set('page', pageNumber.toString());
    return `/?${params.toString()}`;
  };

  return (
    <main className="min-h-screen bg-[#020617] p-4 md:p-8">
      <div className="max-w-7xl mx-auto space-y-8">
        
        {/* HEADER */}
        <header className="flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div>
            <h1 className="text-4xl font-black text-white tracking-tight">Smart Buy <span className="text-emerald-500">Sentinel</span></h1>
            <p className="text-slate-400 mt-1">Intelligence de marché • {pagination.totalDeals} opportunités actives</p>
          </div>
        </header>

        {/* FILTRES */}
        <div className="flex gap-2">
            <HorizontalFilterBar options={filterOptions} />
        </div>

        {/* SECTION STATS */}
        <section className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <KpiCard label="Offres Actives" value={pagination.totalDeals.toString()} />
          <KpiCard label="Prix Moyen" value={`${stats.avgPrice.toFixed(0)}€`} />
          <KpiCard label="Meilleur Prix" value={`${stats.bestPrice.toFixed(0)}€`} accent="emerald" />
          <KpiCard label="Profit Moyen" value={`+${stats.avgProfit.toFixed(0)}€`} accent="green" />
        </section>

        {/* BEST DEAL */}
        <BestDeal deals={deals} />

        {/* LISTE DES DEALS */}
        <section>
          <h2 className="text-xl font-bold text-white mb-6 flex items-center gap-2">
            📊 Flux d'opportunités
          </h2>
          <DealList deals={deals} />
          
          {/* PAGINATION INTÉGRÉE (S'affiche uniquement s'il y a plus d'une page) */}
          {pagination.totalPages > 1 && (
            <div className="flex items-center justify-center gap-4 mt-12 py-4">
              {/* Bouton Précédent */}
              {pagination.currentPage > 1 ? (
                <Link 
                  href={createPageURL(pagination.currentPage - 1)}
                  className="flex items-center gap-2 px-4 py-2 bg-slate-900 border border-slate-800 text-white rounded-lg hover:bg-slate-800 transition-all"
                >
                  <ChevronLeft size={16} /> Précédent
                </Link>
              ) : (
                <div className="flex items-center gap-2 px-4 py-2 bg-slate-900/50 border border-slate-800/50 text-slate-500 rounded-lg cursor-not-allowed">
                  <ChevronLeft size={16} /> Précédent
                </div>
              )}

              {/* Indicateur de page */}
              <span className="text-slate-400 text-sm font-medium">
                Page <span className="text-white font-bold">{pagination.currentPage}</span> sur {pagination.totalPages}
              </span>

              {/* Bouton Suivant */}
              {pagination.currentPage < pagination.totalPages ? (
                <Link 
                  href={createPageURL(pagination.currentPage + 1)}
                  className="flex items-center gap-2 px-4 py-2 bg-slate-900 border border-slate-800 text-white rounded-lg hover:bg-slate-800 transition-all"
                >
                  Suivant <ChevronRight size={16} />
                </Link>
              ) : (
                <div className="flex items-center gap-2 px-4 py-2 bg-slate-900/50 border border-slate-800/50 text-slate-500 rounded-lg cursor-not-allowed">
                  Suivant <ChevronRight size={16} />
                </div>
              )}
            </div>
          )}
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