import { NextResponse } from 'next/server';
import { connectDB } from '@/lib/mongodb';
import User from '@/models/User';

const WEB_APP_URL = "https://sniper-deals-alerts.vercel.app";

export async function POST(req: Request) {
  const body = await req.json();
  const { message } = body;

  if (!message) return NextResponse.json({ status: 'ok' });

  const chatId = message.chat.id;
  const chatInfo = {
    id: chatId,
    username: message.from?.username || message.chat.title || 'Inconnu',
    firstName: message.from?.first_name || message.chat.title || 'Groupe/Canal'
  };
  const text = message.text || '';

  // 1. Sauvegarde systématique de tout chat qui interagit avec le bot
  await saveChatToDb(chatInfo);

  // 2. Gestion des commandes
  // Détection du /start classique OU du /start app (venant de notre Deep Link)
  if (text.startsWith('/start')) {
    
    // Si l'utilisateur vient d'un groupe via le lien "Lancer la Mini-App"
    if (text === '/start app') {
      await fetch(`https://api.telegram.org/bot${process.env.TELEGRAM_BOT_TOKEN}/sendMessage`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          chat_id: chatId,
          text: "C'est parti ! Voici ta Mini-App :",
          reply_markup: {
            inline_keyboard: [[
              { text: "🚀 Ouvrir la Mini-App", web_app: { url: WEB_APP_URL } }
            ]]
          }
        })
      });
    } 
    // Sinon : Accueil standard
    else {
      await fetch(`https://api.telegram.org/bot${process.env.TELEGRAM_BOT_TOKEN}/sendMessage`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          chat_id: chatId,
          text: "Bienvenue ! Je t'enverrai les meilleures opportunités ici.",
          reply_markup: {
            inline_keyboard: [[
              { text: "🚀 Ouvrir la Mini-App", web_app: { url: WEB_APP_URL } }
            ]]
          }
        })
      });
    }
  }

  return NextResponse.json({ status: 'ok' });
}

async function saveChatToDb(chatInfo: any) {
  try {
    await connectDB();
    await User.findOneAndUpdate(
      { telegramId: chatInfo.id },
      { 
        $set: {
          username: chatInfo.username, 
          firstName: chatInfo.firstName,
          lastSeen: new Date()
        }
      },
      { upsert: true, new: true }
    );
    console.log(`✅ Chat ${chatInfo.id} synchronisé.`);
  } catch (error) {
    console.error('❌ Erreur Mongoose :', error);
  }
}