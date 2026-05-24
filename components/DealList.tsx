import { DealCard } from '@/components/DealCard';
import { IDeal } from '@/models/Deal';

export const DealList = ({ deals }: { deals: IDeal[] }) => {
  if (!deals || deals.length === 0) {
    return (
      <div className="bg-slate-900/30 border border-dashed border-slate-800 rounded-2xl p-12 text-center text-slate-500">
        <p className="text-4xl mb-2">🔍</p>
        <p className="font-semibold text-white">Aucun deal trouvé</p>
        <p className="text-sm">Ajustez vos filtres pour voir les opportunités.</p>
      </div>
    );
  }

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
      {deals.map((deal) => (
        <DealCard key={String(deal._id)} deal={deal} />
      ))}
    </div>
  );
};