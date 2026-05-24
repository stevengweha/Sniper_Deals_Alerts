import { NextResponse } from 'next/server';
import { connectDB } from '@/lib/mongodb';
import User from '@/models/User';

const BOT_TOKEN = process.env.TELEGRAM_BOT_TOKEN;
const WEB_APP_URL = "https://sniper-deals-alerts.vercel.app";

// Fonction utilitaire pour envoyer des messages proprement
async function sendTelegramMessage(chatId: number, text: string) {
  return fetch(`https://api.telegram.org/bot${BOT_TOKEN}/sendMessage`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      chat_id: chatId,
      text,
      reply_markup: {
        inline_keyboard: [[
          { text: "🚀 Accéder au Scanner de Deals", web_app: { url: WEB_APP_URL } }
        ]]
      }
    })
  });
}

export async function POST(req: Request) {
  try {
    const { message } = await req.json();
    if (!message?.chat?.id) return NextResponse.json({ status: 'ok' });

    const chatId = message.chat.id;
    const text = message.text || '';

    // Sauvegarde en arrière-plan sans bloquer la réponse
    saveChatToDb({
      id: chatId,
      username: message.from?.username || message.chat.title || 'Inconnu',
      firstName: message.from?.first_name || message.chat.title || 'Groupe/Canal'
    }).catch(console.error);

    // Gestion des commandes
    if (text.startsWith('/start')) {
      const isDeepLink = text === '/start app';
      const welcomeMessage = isDeepLink 
        ? "🎯 Accès direct activé ! Ton scanner d'opportunités est prêt."
        : "👋 Bienvenue sur Smart Buy Sentinel !\n\nJe surveille les meilleures opportunités pour toi. Utilise le bouton ci-dessous pour lancer le scanner.";
      
      await sendTelegramMessage(chatId, welcomeMessage);
    }

    return NextResponse.json({ status: 'ok' });
  } catch (err) {
    console.error('❌ Erreur Webhook :', err);
    return NextResponse.json({ status: 'error' }, { status: 500 });
  }
}

async function saveChatToDb(chatInfo: any) {
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
    { upsert: true }
  );
  console.log(`✅ Chat ${chatInfo.id} synchronisé.`);
}