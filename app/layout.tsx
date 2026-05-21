import Script from 'next/script';
import './globals.css';
import { TelegramProvider } from '@/components/TelegramProvider';

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="fr" className="dark">
      <head>
        {/* Le script est chargé avant tout pour que le provider puisse l'utiliser */}
        <Script 
          src="https://telegram.org/js/telegram-web-app.js" 
          strategy="beforeInteractive" 
        />
      </head>
      <body className="bg-slate-950">
        <TelegramProvider>
          {children}
        </TelegramProvider>
      </body>
    </html>
  );
}