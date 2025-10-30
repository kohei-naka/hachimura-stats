# tools/fetch_hachimura.py
import json, os, time
from datetime import datetime
import requests

# balldontlie の season は「開始年」（例：2024-25シーズンなら 2024）
SEASON = int(os.getenv("SEASON", "2024"))
PLAYER_NAME = os.getenv("PLAYER_NAME", "Rui Hachimura")
OUT_PATH = os.getenv("OUT_PATH", "docs/data/games.json")
API_BASE = os.getenv("BALDONTLIE_API_BASE", "https://api.balldontlie.io/v1")
# API_KEY = os.getenv("BALDONTLIE_API_KEY")  # もし必要なら Secrets で設定（無ければ未使用）

# HEADERS = {"Authorization": API_KEY} if API_KEY else {}

API_KEY = os.getenv("BALDONTLIE_API_KEY")

def api_headers():
    if not API_KEY:
        return {}
    return {
        "Authorization": f"Bearer {API_KEY}",
    }

def api_params(extra: dict = None):
    return extra or {}

def get_player_id(name: str) -> int:
    # "Rui Hachimura" → "Hachimura"
    last = name.split()[-1]
    r = requests.get(
        f"{API_BASE}/players",
        params=api_params({"search": last, "per_page": 100}),
        headers=api_headers(),
        timeout=20
    )
    r.raise_for_status()
    data = r.json()["data"]

    for p in data:
        full = f"{p.get('first_name','')} {p.get('last_name','')}".strip()
        if full.lower() == name.lower():
            return p["id"]

    if not data:
        raise RuntimeError(f"player not found: {name}")

    # フルネーム一致が無くても、とりあえず先頭を返す
    return data[0]["id"]

def list_stats(player_id: int, season: int):
    page, per_page = 1, 100
    out = []
    while True:
        r = requests.get(
        f"{API_BASE}/stats",
        params=api_params({
            "player_ids[]": player_id,
            "seasons[]": season,
            "per_page": per_page,
            "page": page
        }),
        headers=api_headers(),
        timeout=30
)
        r.raise_for_status()
        js = r.json()
        out.extend(js["data"])
        if page >= js["meta"]["total_pages"]:
            break
        page += 1
        time.sleep(0.2)
    return out

def mmss_to_minutes(mmss: str) -> int:
    if not mmss or ":" not in mmss: return 0
    m, _s = mmss.split(":")
    return int(m)

def extract_games(stats_raw):
    # 所属チーム略称は最新行から推定（保険）
    latest_team = stats_raw[0]["team"]["abbreviation"] if stats_raw else "LAL"
    games = {}
    for row in stats_raw:
        g = row["game"]
        date = g["date"][:10]  # YYYY-MM-DD
        home_abbr = g["home_team"]["abbreviation"]
        away_abbr = g["visitor_team"]["abbreviation"]
        team_abbr = row.get("team", {}).get("abbreviation", latest_team)

        if team_abbr == home_abbr:
            location, opponent = "home", away_abbr
        elif team_abbr == away_abbr:
            location, opponent = "away", home_abbr
        else:
            # 稀に一致しない場合のフォールバック
            location, opponent = "home", away_abbr

        key = (date, opponent, location)
        prev = games.get(key, {"min":0,"pts":0,"reb":0,"ast":0,"fga":0,"fgm":0,"fg3a":0,"fg3m":0,"fta":0,"ftm":0})
        games[key] = {
            "date": date,
            "opponent": opponent,
            "location": location,
            "min": prev["min"] + mmss_to_minutes(row.get("min") or "0:00"),
            "pts": prev["pts"] + int(row.get("pts") or 0),
            "reb": prev["reb"] + int(row.get("reb") or 0),
            "ast": prev["ast"] + int(row.get("ast") or 0),
            "fga": prev["fga"] + int(row.get("fga") or 0),
            "fgm": prev["fgm"] + int(row.get("fgm") or 0),
            "fg3a": prev["fg3a"] + int(row.get("fg3a") or 0),
            "fg3m": prev["fg3m"] + int(row.get("fg3m") or 0),
            "fta": prev["fta"] + int(row.get("fta") or 0),
            "ftm": prev["ftm"] + int(row.get("ftm") or 0),
        }
    out = list(games.values())
    out.sort(key=lambda x: x["date"], reverse=True)
    return out

def main():
    player_id = get_player_id(PLAYER_NAME)
    stats = list_stats(player_id, SEASON)
    games = extract_games(stats)
    os.makedirs(os.path.dirname(OUT_PATH), exist_ok=True)
    with open(OUT_PATH, "w", encoding="utf-8") as f:
        json.dump(games, f, ensure_ascii=False, indent=2)
    print(f"✅ wrote {len(games)} games to {OUT_PATH}")

if __name__ == "__main__":
    main()
