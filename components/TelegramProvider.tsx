'use client';

import { createContext, useContext, useEffect, useState, useMemo } from 'react';

// On définit un type pour le WebApp afin d'éviter les `any` partout
interface TelegramWebApp {
  ready: () => void;
  expand: () => void;
  HapticFeedback: { impactOccurred: (style: string) => void };
  openLink: (url: string) => void;
  // Ajoute d'autres méthodes au besoin
}

const TelegramContext = createContext<{ webApp: TelegramWebApp | null; isReady: boolean }>({
  webApp: null,
  isReady: false,
});

export const TelegramProvider = ({ children }: { children: React.ReactNode }) => {
  const [webApp, setWebApp] = useState<TelegramWebApp | null>(null);

  useEffect(() => {
    // Vérification de sécurité pour le SSR (Next.js)
    if (typeof window !== 'undefined') {
      const tg = (window as any).Telegram?.WebApp;
      if (tg) {
        tg.ready();
        tg.expand();
        setWebApp(tg);
      }
    }
  }, []);

  // useMemo évite de recalculer l'objet context à chaque rendu
  const value = useMemo(() => ({
    webApp,
    isReady: !!webApp
  }), [webApp]);

  return (
    <TelegramContext.Provider value={value}>
      {children}
    </TelegramContext.Provider>
  );
};

export const useTelegram = () => useContext(TelegramContext);