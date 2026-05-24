import mongoose, { Document, Schema, Model } from 'mongoose';

export interface IDeal extends Document {
  _id: mongoose.Types.ObjectId;
  title: string;
  url: string;
  price: number;
  category: string;
  estimated_resell_profit: number;
  deal_score: string;
  operational_status: string;
  z_score: number;
  product_condition: string;
  product_model?: string;
  brand?: string;
  storage_capacity?: string;
  image_url?: string;
  data_age_hours?: number;
  source?: string;
  median_model_price?: number;
  pct_deviation?: number;
  statistical_confidence?: string; // Ajout du champ de confiance statistique (ex: "🟢 Haute", "🟡 Modérée", "🔴 Faible")
}

const dealSchema = new Schema<IDeal>({
  title: { type: String },
  url: { type: String },
  price: { type: Number },
  category: { type: String },
  estimated_resell_profit: { type: Number },
  deal_score: { type: String },
  operational_status: { type: String },
  z_score: { type: Number },
  product_condition: { type: String },
    product_model: { type: String },
    brand: { type: String },
  image_url: { type: String },
  data_age_hours: { type: Number },
  source: { type: String },
  median_model_price: { type: Number },
  pct_deviation: { type: Number },
  statistical_confidence: { type: String },
}, { strict: false });

export const Deal: Model<IDeal> = mongoose.models.Deal || mongoose.model<IDeal>('Deal', dealSchema);