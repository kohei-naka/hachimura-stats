
from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import json
from pathlib import Path
from statistics import mean
import os, urllib.request

DATA_FILE = Path(__file__).parent.parent / "data" / "games_2024_25.json"

def calc_efg(fgm: int, fg3m: int, fga: int) -> Optional[float]:
    if fga == 0:
        return None
    return (fgm + 0.5 * fg3m) / fga

def calc_ts(pts: int, fga: int, fta: int) -> Optional[float]:
    denom = 2 * (fga + 0.44 * fta)
    if denom == 0:
        return None
    return pts / denom

class Game(BaseModel):
    date: str
    opponent: str
    location: str
    min: int
    pts: int
    reb: int
    ast: int
    fga: int
    fgm: int
    fg3a: int
    fg3m: int
    fta: int
    ftm: int
    efg: Optional[float] = None
    ts: Optional[float] = None

class SeasonAvg(BaseModel):
    season: str
    gp: int
    mpg: float
    ppg: float
    rpg: float
    apg: float
    efg: Optional[float]
    ts: Optional[float]

app = FastAPI(title="Hachimura Stats API", version="0.1.0")

# CORS - allow local frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
def health():
    return {"ok": True}

def load_games() -> List[Game]:
    # 1) 環境変数 DATA_URL が指定されていれば、そこから取得
    data_url = os.environ.get("DATA_URL")
    raw = None
    if data_url:
        try:
            with urllib.request.urlopen(data_url, timeout=10) as r:
                raw = r.read().decode("utf-8")
        except Exception:
            raw = None  # 失敗したらローカルへフォールバック

    # 2) フォールバック：ローカルのサンプルJSON
    if raw is None:
        raw = DATA_FILE.read_text(encoding="utf-8")

    data = json.loads(raw)
    games: List[Game] = []
    for g in data:
        efg = calc_efg(g["fgm"], g["fg3m"], g["fga"])
        ts = calc_ts(g["pts"], g["fga"], g["fta"])
        games.append(Game(**g, efg=efg, ts=ts))
    return games

@app.get("/hachimura/games", response_model=List[Game])
def get_games(limit: int = Query(20, ge=1, le=100)):
    games = load_games()
    games_sorted = sorted(games, key=lambda x: x.date, reverse=True)
    return games_sorted[:limit]

@app.get("/hachimura/season-avg", response_model=SeasonAvg)
def season_avg(season: str = "2024-25"):
    games = load_games()
    if not games:
        return SeasonAvg(season=season, gp=0, mpg=0, ppg=0, rpg=0, apg=0, efg=None, ts=None)
    gp = len(games)
    mpg = mean([g.min for g in games])
    ppg = mean([g.pts for g in games])
    rpg = mean([g.reb for g in games])
    apg = mean([g.ast for g in games])
    # For eFG/TS season average we use shot-sum then formula (= more correct than averaging percentages)
    sum_fga = sum(g.fga for g in games)
    sum_fgm = sum(g.fgm for g in games)
    sum_fg3m = sum(g.fg3m for g in games)
    sum_pts = sum(g.pts for g in games)
    sum_fta = sum(g.fta for g in games)

    efg_val = None if sum_fga == 0 else (sum_fgm + 0.5 * sum_fg3m) / sum_fga
    ts_val = None
    denom = 2 * (sum_fga + 0.44 * sum_fta)
    if denom > 0:
        ts_val = sum_pts / denom

    return SeasonAvg(
        season=season,
        gp=gp,
        mpg=round(mpg, 1),
        ppg=round(ppg, 1),
        rpg=round(rpg, 1),
        apg=round(apg, 1),
        efg=efg_val,
        ts=ts_val,
    )
