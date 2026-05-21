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
    await connectDB(); // Assure la connexion
    
    await user.findOneAndUpdate(
      { telegramId: user.id },
      { 
        username: user.username, 
        firstName: user.first_name,
        lastSeen: new Date()
      },
      { upsert: true, new: true } // Upsert gère la création ou la mise à jour
    );
    
    console.log(`✅ User ${user.id} synchronisé avec le modèle Mongoose.`);
  } catch (error) {
    console.error('❌ Erreur Mongoose :', error);
  }
}