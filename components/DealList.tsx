import { DealCard } from '@/components/DealCard';
import { IDeal } from '@/models/Deal';

export const DealList = ({ deals }: { deals: IDeal[] }) => {
  if (!deals || deals.length === 0) {
    return (
      <div className="text-center text-slate-400 p-8">
        <p className="text-lg">🔍 Aucun deal trouvé</p>
        <p className="text-sm">Essayez d'ajuster vos filtres</p>
      </div>
    );
  }

  return (
    <div className="space-y-3 px-2 pb-20">
      {deals.map((deal) => (
        <DealCard key={String(deal._id)} deal={deal} />
      ))}
    </div>
  );
};