'use client';

import { useEffect } from 'react';

export const TelegramProvider = ({ children }: { children: React.ReactNode }) => {
  useEffect(() => {
    // Initialisation du WebApp Telegram
    const initTelegram = async () => {
      if (typeof window !== 'undefined' && (window as any).Telegram?.WebApp) {
        const tg = (window as any).Telegram.WebApp;
        tg.ready(); // Informe Telegram que l'app est chargée
        tg.expand(); // Ouvre l'app en plein écran
        // Applique le thème de l'utilisateur
        document.documentElement.className = tg.colorScheme === 'dark' ? 'dark' : '';
      }
    };
    initTelegram();
  }, []);

  return <>{children}</>;
};