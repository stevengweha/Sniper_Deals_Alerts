'use server';

import { connectDB } from '@/lib/mongodb';
import { Deal } from '@/models/Deal';

export async function getDashboardData(filters: any = {}, page = 1, limit = 20) {
  await connectDB();

  // 1. Construction dynamique de la requête
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

  // 2. Exécution parallèle optimisée avec récupération des filtres globaux
  const [deals, statsResult, categories, brands, models, totalDeals] = await Promise.all([
    // Pagination : on ne récupère que le nombre limité d'éléments
    Deal.find(query)
      .sort({ timestamp: -1 })
      .skip((page - 1) * limit)
      .limit(limit)
      .lean(),
    
    // Agrégation : le calcul est fait par MongoDB
    Deal.aggregate([
      { $match: query },
      { $group: {
          _id: null,
          avgPrice: { $avg: "$price" },
          bestPrice: { $min: "$price" },
          avgProfit: { $avg: "$estimated_resell_profit" },
          bestProfit: { $max: "$estimated_resell_profit" },
          totalPotentialProfit: { $sum: "$estimated_resell_profit" }
      }}
    ]),
    
    // Récupération globale pour remplir les menus du filtre (indépendant de la pagination)
    Deal.distinct("category"),
    Deal.distinct("brand"),
    Deal.distinct("product_model"),
    
    // Nombre total de documents pour la pagination
    Deal.countDocuments(query)
  ]);

  return {
    deals: JSON.parse(JSON.stringify(deals)),
    // On regroupe les options de filtrage dans un seul objet propre
    filterOptions: {
      categories: categories || [],
      brands: brands || [],
      models: models || []
    },
    stats: statsResult[0] || { avgPrice: 0, bestPrice: 0, avgProfit: 0, bestProfit: 0, totalPotentialProfit: 0 },
    pagination: {
      totalDeals: totalDeals || 0,
      currentPage: page,
      totalPages: Math.ceil((totalDeals || 0) / limit)
    }
  };
}