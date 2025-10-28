
"use client";

import { useEffect, useState } from "react";
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from "recharts";

type Game = {
  date: string;
  opponent: string;
  location: string;
  min: number;
  pts: number;
  reb: number;
  ast: number;
  fga: number;
  fgm: number;
  fg3a: number;
  fg3m: number;
  fta: number;
  ftm: number;
  efg?: number | null;
  ts?: number | null;
};

const API = process.env.NEXT_PUBLIC_API_BASE || "http://localhost:8000";

export default function Page() {
  const [games, setGames] = useState<Game[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    (async () => {
      try {
        const res = await fetch(`${API}/hachimura/games?limit=20`);
        if (!res.ok) throw new Error(`HTTP ${res.status}`);
        const data = await res.json();
        setGames(data);
      } catch (e: any) {
        setError(e.message);
      } finally {
        setLoading(false);
      }
    })();
  }, []);

  const latest = games[0];

  return (
    <main className="space-y-4">
      <section className="card">
        <h2 className="text-lg font-semibold mb-2">直近試合</h2>
        {loading && <p>読み込み中…</p>}
        {error && <p className="text-red-500">エラー: {error}</p>}
        {!loading && !error && latest && (
          <div className="grid grid-cols-2 gap-2 text-sm">
            <div><span className="sub">日付</span><div>{latest.date}</div></div>
            <div><span className="sub">対戦</span><div>{latest.location === "home" ? "vs" : "@"} {latest.opponent}</div></div>
            <div><span className="sub">PTS / REB / AST</span><div>{latest.pts} / {latest.reb} / {latest.ast}</div></div>
            <div><span className="sub">TS% / eFG%</span>
              <div>{(latest.ts ?? 0 * 100).toFixed(1)}% / {(latest.efg ?? 0 * 100).toFixed(1)}%</div>
            </div>
            <div><span className="sub">FG</span><div>{latest.fgm}-{latest.fga}</div></div>
            <div><span className="sub">3PT / FT</span><div>{latest.fg3m}-{latest.fg3a} / {latest.ftm}-{latest.fta}</div></div>
          </div>
        )}
      </section>

      <section className="card">
        <h2 className="text-lg font-semibold mb-2">得点推移（直近）</h2>
        <div className="h-64">
          <ResponsiveContainer width="100%" height="100%">
            <LineChart data={[...games].reverse()} margin={{ top: 10, right: 20, left: 0, bottom: 0 }}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="date" />
              <YAxis />
              <Tooltip />
              <Line type="monotone" dataKey="pts" dot={false} />
            </LineChart>
          </ResponsiveContainer>
        </div>
      </section>
    </main>
  );
}
