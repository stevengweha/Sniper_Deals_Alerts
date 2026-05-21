'use client';

import { useEffect, createContext, useContext, useState } from 'react';

const TelegramContext = createContext<boolean>(false);

export const TelegramProvider = ({ children }: { children: React.ReactNode }) => {
  const [isReady, setIsReady] = useState(false);

  useEffect(() => {
    if (typeof window !== 'undefined' && (window as any).Telegram?.WebApp) {
      const tg = (window as any).Telegram.WebApp;
      tg.ready();
      tg.expand();
      setIsReady(true);
    }
  }, []);

  return (
    <TelegramContext.Provider value={isReady}>
      {children}
    </TelegramContext.Provider>
  );
};

export const useTelegram = () => useContext(TelegramContext);