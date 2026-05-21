import { connectDB } from './mongodb';
import { Deal } from '@/models/Deal';

export async function getDashboardData(filters: {
  category?: string;
  brand?: string;
  product_model?: string;
  storage_capacity?: string;
  source?: string;
  product_condition?: string;
  minPrice?: number;
  maxPrice?: number;
  search?: string;
} = {}) {
  await connectDB();

  const query: any = { operational_status: '🟢 Actif' };

  if (filters.category && filters.category !== 'Tous' && filters.category !== 'All') {
    query.category = filters.category;
  }
  if (filters.brand && filters.brand !== 'Tous' && filters.brand !== 'All') {
    query.brand = filters.brand;
  }
  if (filters.product_model && filters.product_model !== 'Tous' && filters.product_model !== 'All') {
    query.product_model = filters.product_model;
  }
  if (filters.storage_capacity && filters.storage_capacity !== 'Toutes' && filters.storage_capacity !== 'All') {
    query.storage_capacity = filters.storage_capacity;
  }
  if (filters.source && filters.source !== 'All') {
    query.source = filters.source;
  }
  if (filters.product_condition && filters.product_condition !== 'Tous' && filters.product_condition !== 'All') {
    query.product_condition = filters.product_condition;
  }

  if (typeof filters.minPrice === 'number' || typeof filters.maxPrice === 'number') {
    query.price = {};
    if (typeof filters.minPrice === 'number') query.price.$gte = filters.minPrice;
    if (typeof filters.maxPrice === 'number') query.price.$lte = filters.maxPrice;
  }

  if (filters.search && String(filters.search).trim().length > 0) {
    const safeSearch = String(filters.search).replace(/[-[\]{}()*+?.,\\^$|#\s]/g, '\\$&');
    const regex = new RegExp(safeSearch, 'i');
    query.$or = [
      { title: regex },
      { product_model: regex },
      { brand: regex },
    ];
  }

  const deals = await Deal.find(query)
    .sort({ estimated_resell_profit: -1, z_score: -1 })
    .limit(100)
    .lean();

  return JSON.parse(JSON.stringify(deals));
}