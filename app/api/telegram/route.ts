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
      parse_mode: 'Markdown',
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

    // 1. Connexion DB et vérification si l'utilisateur est nouveau
    await connectDB();
    const userExists = await User.exists({ telegramId: chatId });

    // 2. Sauvegarde ou mise à jour des infos utilisateur
    await saveChatToDb({
      id: chatId,
      username: message.from?.username || message.chat.title || 'Inconnu',
      firstName: message.from?.first_name || message.chat.title || 'Groupe/Canal'
    });

    // 3. Gestion des commandes
    if (text.startsWith('/start')) {
      // On n'envoie le message de bienvenue QUE si l'utilisateur est nouveau
      if (!userExists) {
        const isDeepLink = text === '/start app';
        const welcomeMessage = `👋 Bienvenue sur Smart Buy Sentinel !\n\n` +
          `Je suis ton assistant personnel pour dénicher les meilleures opportunités du marché.\n\n` +
          `🚀 **Ce que je fais pour toi :**\n` +
          `• Surveillance en temps réel des prix.\n` +
          `• Détection automatique de deals ultra-rentables.\n` +
          `• Analyse rapide pour t'aider à décider en un clin d'œil.\n\n` +
          `${isDeepLink ? "🎯 Accès direct activé !" : "Utilise le bouton ci-dessous pour lancer la Mini-App et commencer à économiser !"}`;
        
        await sendTelegramMessage(chatId, welcomeMessage);
      }
    }

    return NextResponse.json({ status: 'ok' });
  } catch (err) {
    console.error('❌ Erreur Webhook :', err);
    return NextResponse.json({ status: 'error' }, { status: 500 });
  }
}

async function saveChatToDb(chatInfo: any) {
  try {
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
  } catch (error) {
    console.error('❌ Erreur Mongoose :', error);
  }
}