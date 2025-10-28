
export const metadata = {
  title: "RuiStats",
  description: "八村塁スタッツ（Dockerテンプレ）",
};

import "./../styles/globals.css";

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="ja">
      <body>
        <div className="max-w-3xl mx-auto p-4 space-y-4">
          <header className="flex items-center justify-between">
            <h1 className="h1">RuiStats</h1>
            <a className="sub underline" href="/season">シーズン平均</a>
          </header>
          {children}
          <footer className="sub text-center py-8 opacity-60">
            Dockerテンプレ / Next.js + FastAPI
          </footer>
        </div>
      </body>
    </html>
  );
}
