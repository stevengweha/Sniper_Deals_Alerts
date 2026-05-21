import mongoose from 'mongoose';

/**
 * MongoDB Connection Manager avec caching global
 * Évite les reconnexions multiples en environnement serverless
 */

interface MongooseConnection {
  conn: typeof mongoose | null;
  promise: Promise<typeof mongoose> | null;
}

// Variable globale pour stocker la connexion (compatible avec Hot Reload Next.js)
declare global {
  var mongooseConnection: MongooseConnection | undefined;
}

let cached: MongooseConnection = global.mongooseConnection || {
  conn: null,
  promise: null,
};

if (!global.mongooseConnection) {
  global.mongooseConnection = cached;
}

export async function connectDB(): Promise<typeof mongoose> {
  if (cached.conn) {
    console.log('📦 Utilisant connexion MongoDB en cache');
    return cached.conn;
  }

  if (!cached.promise) {
    const opts = {
      bufferCommands: false,
      maxPoolSize: 10,
      serverSelectionTimeoutMS: 5000,
      socketTimeoutMS: 45000,
    };

    const mongoUri = process.env.MONGODB_URI;

    if (!mongoUri) {
      throw new Error(
        '❌ MONGODB_URI est manquant dans les variables d\'environnement'
      );
    }

    console.log('🔌 Connexion à MongoDB...');

    cached.promise = mongoose
      .connect(mongoUri, opts)
      .then((mongoose) => {
        console.log('✅ MongoDB connecté avec succès');
        return mongoose;
      })
      .catch((error) => {
        console.error('❌ Erreur MongoDB:', error.message);
        cached.promise = null;
        throw error;
      });
  }

  try {
    cached.conn = await cached.promise;
  } catch (error) {
    cached.promise = null;
    throw error;
  }

  return cached.conn;
}

export async function disconnectDB(): Promise<void> {
  if (cached.conn) {
    await mongoose.disconnect();
    cached.conn = null;
    cached.promise = null;
    console.log('🔌 MongoDB déconnecté');
  }
}

export function isConnected(): boolean {
  return cached.conn !== null && mongoose.connection.readyState === 1;
}
