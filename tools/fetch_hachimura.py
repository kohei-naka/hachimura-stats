# tools/fetch_hachimura.py
import os, json, time, requests

OUT_PATH = os.getenv("OUT_PATH", "docs/data/games.json")
SEASON = os.getenv("SEASON", "2024")            # 2024-25
PLAYER_NAME = os.getenv("PLAYER_NAME", "Rui Hachimura")

RAPID_KEY = os.getenv("RAPIDAPI_KEY")
RAPID_HOST = "api-nba-v1.p.rapidapi.com"
BASE = f"https://{RAPID_HOST}"
HEADERS = {"X-RapidAPI-Key": RAPID_KEY, "X-RapidAPI-Host": RAPID_HOST}

def rget(path, params=None, retry=3, wait=2):
    url = f"{BASE}{path}"
    last = None
    for i in range(retry):
        r = requests.get(url, headers=HEADERS, params=params or {}, timeout=30)
        if r.status_code == 429:  # レート制限
            time.sleep(wait*(i+1)); last = r; continue
        try:
            r.raise_for_status(); return r.json()
        except requests.HTTPError:
            last = r
            if 500 <= r.status_code < 600:
                time.sleep(wait*(i+1)); continue
            raise
    raise requests.HTTPError(f"request failed: {last.status_code} {last.text[:200]}")

def find_player(fullname: str):
    last = fullname.split()[-1]
    data = rget("/players", {"search": last})
    for p in data.get("response", []):
        fn = f"{p.get('firstname','')} {p.get('lastname','')}".strip()
        if fn.lower() == fullname.lower(): return p
    return data.get("response", [None])[0]

def list_stats(player_id: int, season: str):
    page = 1; out = []
    while True:
        data = rget("/players/statistics", {"id": player_id, "season": season, "page": page})
        resp = data.get("response", [])
        if not resp: break
        for g in resp:
            game = g.get("game", {}) or {}
            out.append({
                "date": (game.get("date") or {}).get("start") if isinstance(game.get("date"), dict) else game.get("date"),
                "opponent": (g.get("team") or {}).get("name"),
                "pts": g.get("points"), "reb": g.get("totReb"), "ast": g.get("assists"),
                "stl": g.get("steals"), "blk": g.get("blocks"), "tov": g.get("turnovers"),
                "fgm": g.get("fgm"), "fga": g.get("fga"),
                "fg3m": g.get("tpm") or g.get("threePointsMade"),
                "fg3a": g.get("tpa") or g.get("threePointsAttempted"),
                "ftm": g.get("ftm"), "fta": g.get("fta"),
                "min": g.get("min"),
            })
        page += 1
        if page > 40: break  # 安全ブレーキ
    return out

def main():
    if not RAPID_KEY: raise RuntimeError("RAPIDAPI_KEY is not set")
    player = find_player(PLAYER_NAME)
    if not player: raise RuntimeError(f"player not found: {PLAYER_NAME}")
    pid = player.get("id") or (player.get("player") or {}).get("id")
    if not pid: raise RuntimeError("player id missing from API-NBA response")

    print(f"DEBUG: player_id={pid} season={SEASON}")
    stats = list_stats(pid, SEASON)
    print(f"DEBUG: fetched {len(stats)} games")

    os.makedirs(os.path.dirname(OUT_PATH), exist_ok=True)
    with open(OUT_PATH, "w", encoding="utf-8") as f:
        json.dump(stats, f, ensure_ascii=False, indent=2)
    print(f"✅ wrote {len(stats)} games to {OUT_PATH}")

if __name__ == "__main__":
    main()
