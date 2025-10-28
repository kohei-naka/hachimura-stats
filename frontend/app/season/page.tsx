
"use client";

import { useEffect, useState } from "react";

type SeasonAvg = {
  season: string;
  gp: number;
  mpg: number;
  ppg: number;
  rpg: number;
  apg: number;
  efg?: number | null;
  ts?: number | null;
};

const API = process.env.NEXT_PUBLIC_API_BASE || "http://localhost:8000";

export default function Page() {
  const [avg, setAvg] = useState<SeasonAvg | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    (async () => {
      try {
        const res = await fetch(`${API}/hachimura/season-avg?season=2024-25`);
        if (!res.ok) throw new Error(`HTTP ${res.status}`);
        const data = await res.json();
        setAvg(data);
      } catch (e: any) {
        setError(e.message);
      } finally {
        setLoading(false);
      }
    })();
  }, []);

  return (
    <main className="card">
      <h2 className="text-lg font-semibold mb-2">シーズン平均</h2>
      {loading && <p>読み込み中…</p>}
      {error && <p className="text-red-500">エラー: {error}</p>}
      {avg && (
        <div className="grid grid-cols-2 gap-2 text-sm">
          <div><span className="sub">シーズン</span><div>{avg.season}</div></div>
          <div><span className="sub">試合数</span><div>{avg.gp}</div></div>
          <div><span className="sub">MPG</span><div>{avg.mpg}</div></div>
          <div><span className="sub">PPG</span><div>{avg.ppg}</div></div>
          <div><span className="sub">RPG</span><div>{avg.rpg}</div></div>
          <div><span className="sub">APG</span><div>{avg.apg}</div></div>
          <div><span className="sub">TS%</span><div>{avg.ts !== null && avg.ts !== undefined ? (avg.ts * 100).toFixed(1) + "%" : "-"}</div></div>
          <div><span className="sub">eFG%</span><div>{avg.efg !== null && avg.efg !== undefined ? (avg.efg * 100).toFixed(1) + "%" : "-"}</div></div>
        </div>
      )}
    </main>
  );
}
