'use client';

import { useEffect, createContext, useContext } from 'react';

const TelegramContext = createContext<any>(null);

export const TelegramProvider = ({ children }: { children: React.ReactNode }) => {
  useEffect(() => {
    const initTelegram = async () => {
      if (typeof window !== 'undefined' && (window as any).Telegram?.WebApp) {
        const tg = (window as any).Telegram.WebApp;
        tg.ready();
        tg.expand();
        
        // 1. Logique de thème
        document.documentElement.style.backgroundColor = tg.backgroundColor;
        
        // 2. Récupérer l'ID utilisateur pour tes futures fonctions (achat, favoris, etc.)
        const user = tg.initDataUnsafe?.user;
        if (user) {
          console.log("Utilisateur connecté :", user.id);
        }
      }
    };
    initTelegram();
  }, []);

  return <TelegramContext.Provider value={null}>{children}</TelegramContext.Provider>;
};