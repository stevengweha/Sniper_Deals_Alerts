import { NextResponse } from 'next/server';
// Importe ta fonction de connexion DB
import { connectDB } from '@/lib/mongodb' 

const WEB_APP_URL = "https://sniper-deals-alerts.vercel.app";

export async function POST(req: Request) {
  const body = await req.json();
  const { message } = body;

  if (!message) return NextResponse.json({ status: 'ok' });

  const chatId = message.chat.id;
  const user = message.from; // C'est ici que tu as l'ID, username, etc.
  const text = message.text;

  const inlineKeyboard = {
    inline_keyboard: [[
      { text: "🚀 Ouvrir la Mini-App", web_app: { url: WEB_APP_URL } }
    ]]
  };

  if (text === '/start') {
    // 1. Sauvegarde directe dans MongoDB depuis le serveur
    await saveUserToDb(user);

    // 2. Réponse Telegram
    await fetch(`https://api.telegram.org/bot${process.env.TELEGRAM_BOT_TOKEN}/sendMessage`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        chat_id: chatId,
        text: "Bienvenue ! Je t'enverrai les meilleures opportunités ici.",
        reply_markup: inlineKeyboard
      })
    });
  }

  return NextResponse.json({ status: 'ok' });
}

// Fonction Serveur pour MongoDB
// Fonction Serveur pour MongoDB
async function saveUserToDb(user: any) {
  try {
    const db = await connectDB(); // Utilise ta fonction connectDB() importée
    
    // On utilise updateOne avec { upsert: true } pour créer l'utilisateur 
    // s'il n'existe pas, ou mettre à jour ses infos s'il existe déjà.
    await db.collection('users').updateOne(
      { telegramId: user.id },
      { 
        $set: { 
          username: user.username || 'unknown', 
          firstName: user.first_name || 'utilisateur',
          lastSeen: new Date()
        } 
      },
      { upsert: true }
    );
    
    console.log(`✅ User ${user.id} synchronisé en base.`);
  } catch (error) {
    console.error('❌ Erreur lors de la sauvegarde utilisateur :', error);
  }
}