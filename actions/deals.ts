'use server';

import { connectDB } from '@/lib/mongodb';
import { Deal } from '@/models/Deal';

export type DealsFilters = {
  category?: string;
  brand?: string;
  product_model?: string;
  storage_capacity?: string;
  source?: string;
  product_condition?: string;
  minPrice?: number;
  maxPrice?: number;
  search?: string;
  page?: number;
  limit?: number;
};

export async function getDeals(filters: DealsFilters = {}) {
  const {
    category, brand, product_model, storage_capacity,
    source, product_condition, minPrice, maxPrice,
    search, page = 1, limit = 50,
  } = filters;

  try {
    await connectDB();

    const query: any = { operational_status: '🟢 Actif' };

    // Filtres
    if (category && category !== 'Tous' && category !== 'All') query.category = category;
    if (brand && brand !== 'Tous' && brand !== 'All') query.brand = brand;
    if (product_model && product_model !== 'Tous' && product_model !== 'All') query.product_model = product_model;
    if (storage_capacity && storage_capacity !== 'Toutes' && storage_capacity !== 'All') query.storage_capacity = storage_capacity;
    if (source && source !== 'All') query.source = source;
    if (product_condition && product_condition !== 'Tous' && product_condition !== 'All') query.product_condition = product_condition;

    if (typeof minPrice === 'number' || typeof maxPrice === 'number') {
      query.price = {};
      if (typeof minPrice === 'number') query.price.$gte = minPrice;
      if (typeof maxPrice === 'number') query.price.$lte = maxPrice;
    }

    if (search && String(search).trim().length > 0) {
      const safeSearch = String(search).replace(/[-[\]{}()*+?.,\\^$|#\s]/g, '\\$&');
      const regex = new RegExp(safeSearch, 'i');
      query.$or = [{ title: regex }, { product_model: regex }, { brand: regex }];
    }

    // Exécution optimisée : on compte d'abord, puis on récupère les données
    const total = await Deal.countDocuments(query);
    const skip = Math.max(0, (page - 1) * limit);

    // OPTIMISATION : Projection stricte pour alléger le JSON transféré
    // Assure-toi que ces noms de champs correspondent EXACTEMENT à ton modèle Mongoose
    const deals = await Deal.find(query)
      .select('title price estimated_resell_profit url source product_condition deal_score thumbnail')
      .sort({ estimated_resell_profit: -1, z_score: -1 })
      .skip(skip)
      .limit(limit)
      .lean();

    return {
      success: true,
      data: JSON.parse(JSON.stringify(deals)),
      meta: { total, page, limit, count: deals.length },
    };
  } catch (error) {
    console.error('❌ Erreur:', error);
    return { success: false, data: [], error: String(error) };
  }
}