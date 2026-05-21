'use client';

import { useEffect, createContext, useContext, useState } from 'react';

const TelegramContext = createContext<any>(null);

export const TelegramProvider = ({ children }: { children: React.ReactNode }) => {
  const [tgData, setTgData] = useState<any>(null);

  useEffect(() => {
    const initTelegram = async () => {
      if (typeof window !== 'undefined' && (window as any).Telegram?.WebApp) {
        const tg = (window as any).Telegram.WebApp;
        tg.ready();
        tg.expand();

        // Extraction des données de contexte
        const initData = tg.initDataUnsafe;
        
        const context = {
          // Si c'est un user, on prend son ID, sinon on prend l'ID du chat (groupe/canal)
          chatId: initData.user?.id || initData.chat?.id,
          type: initData.chat ? initData.chat.type : 'private', // 'private', 'group', 'supergroup', 'channel'
          userName: initData.user?.first_name || initData.chat?.title || 'Utilisateur',
          isExpanded: tg.isExpanded,
          themeParams: tg.themeParams
        };

        setTgData(context);
        console.log("Context détecté :", context);
      }
    };
    initTelegram();
  }, []);

  return (
    <TelegramContext.Provider value={tgData}>
      {children}
    </TelegramContext.Provider>
  );
};

// Hook personnalisé pour utiliser les données n'importe où
export const useTelegram = () => useContext(TelegramContext);