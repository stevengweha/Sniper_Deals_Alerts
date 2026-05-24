import { connectDB } from './mongodb';
import { Deal } from '@/models/Deal';

export async function getDashboardData(filters: any = {}) {
  await connectDB();

  // 1. Définition de la requête de base (Sans filtre de statut imposé)
  const query: any = {};

  if (filters.category && filters.category !== 'Tous' && filters.category !== 'All') query.category = filters.category;
  if (filters.brand && filters.brand !== 'Tous' && filters.brand !== 'All') query.brand = filters.brand;
  if (filters.product_model && filters.product_model !== 'Tous' && filters.product_model !== 'All') query.product_model = filters.product_model;
  if (filters.source && filters.source !== 'All') query.source = filters.source;
  if (filters.product_condition && filters.product_condition !== 'Tous' && filters.product_condition !== 'All') query.product_condition = filters.product_condition;

  if (filters.minPrice || filters.maxPrice) {
    query.price = {};
    if (filters.minPrice) query.price.$gte = filters.minPrice;
    if (filters.maxPrice) query.price.$lte = filters.maxPrice;
  }

  if (filters.search) {
    const regex = new RegExp(filters.search, 'i');
    query.$or = [{ title: regex }, { product_model: regex }, { brand: regex }];
  }

  // 2. Récupération des données et comptage réel
  // On utilise countDocuments pour le total réel, et on récupère tout (sans .limit)
  const [deals, totalDeals, allDeals] = await Promise.all([
    Deal.find(query).sort({ timestamp: -1 }).lean(), 
    Deal.countDocuments(query),
    Deal.find({}).lean() // Récupère tout pour la sidebar
  ]);

  // 3. Calcul des stats basées sur les résultats retournés
  const avgPrice = totalDeals > 0 ? deals.reduce((acc, d) => acc + (d.price || 0), 0) / totalDeals : 0;
  const bestPrice = totalDeals > 0 ? Math.min(...deals.map(d => d.price || Infinity)) : 0;
  const avgProfit = totalDeals > 0 ? deals.reduce((acc, d) => acc + (d.estimated_resell_profit || 0), 0) / totalDeals : 0;
  const bestProfit = totalDeals > 0 ? Math.max(...deals.map(d => d.estimated_resell_profit || 0)) : 0;
  const totalPotentialProfit = deals.reduce((acc, d) => acc + (d.estimated_resell_profit || 0), 0);
  
  const sourceCounts = deals.reduce((acc: any, d: any) => {
    acc[d.source] = (acc[d.source] || 0) + 1;
    return acc;
  }, {});
  const bestSource = Object.keys(sourceCounts).length > 0 
    ? Object.keys(sourceCounts).reduce((a, b) => sourceCounts[a] > sourceCounts[b] ? a : b) 
    : 'N/A';

  return {
    deals: JSON.parse(JSON.stringify(deals)),
    allDeals: JSON.parse(JSON.stringify(allDeals)),
    stats: {
      totalDeals,
      avgPrice,
      bestPrice: bestPrice === Infinity ? 0 : bestPrice,
      avgProfit,
      bestProfit,
      totalPotentialProfit,
      bestSource
    }
  };
}