import { NextResponse } from 'next/server';
import { connectDB } from '@/lib/mongodb';
import User from '@/models/User';

const WEB_APP_URL = "https://sniper-deals-alerts.vercel.app";

export async function POST(req: Request) {
  const body = await req.json();
  const { message } = body;

  // Si le webhook reçoit autre chose qu'un message (ex: edited_message), on ignore
  if (!message) return NextResponse.json({ status: 'ok' });

  const chatId = message.chat.id;
  // On récupère les infos de l'utilisateur s'il s'agit d'un message privé,
  // sinon on prend les infos du groupe/canal
  const chatInfo = {
    id: chatId,
    username: message.from?.username || message.chat.title || 'Inconnu',
    firstName: message.from?.first_name || message.chat.title || 'Groupe/Canal'
  };
  const text = message.text;

  const inlineKeyboard = {
    inline_keyboard: [[
      { text: "🚀 Ouvrir la Mini-App", web_app: { url: WEB_APP_URL } }
    ]]
  };

  // Gestion du /start (fonctionne aussi en groupe avec /start@NomDuBot)
  if (text && text.startsWith('/start')) {
    // 1. Sauvegarde/Mise à jour en base
    await saveChatToDb(chatInfo);

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

/**
 * Enregistre ou met à jour le chat (User, Groupe ou Canal) en base de données
 */
async function saveChatToDb(chatInfo: any) {
  try {
    await connectDB();
    
    await User.findOneAndUpdate(
      { telegramId: chatInfo.id }, // Utilise l'ID unique du chat (négatif pour groupes)
      { 
        $set: {
          username: chatInfo.username, 
          firstName: chatInfo.firstName,
          lastSeen: new Date()
        }
      },
      { upsert: true, new: true }
    );
    
    console.log(`✅ Chat ${chatInfo.id} (${chatInfo.firstName}) synchronisé.`);
  } catch (error) {
    console.error('❌ Erreur Mongoose lors de la synchronisation :', error);
  }
}