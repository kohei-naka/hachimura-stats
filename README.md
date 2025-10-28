
# Rui Hachimura Stats — Minimal Template (Docker)
Next.js (App Router) + FastAPI + TS%/eFG%（サーバ側集計）

## 前提
- Docker/Docker Compose が導入済み

## 起動
```bash
docker compose up --build
# フロントエンド: http://localhost:3000
# バックエンド:   http://localhost:8000/docs  (FastAPI Swagger)
```

## 構成
- `frontend/` … Next.js 14 + Tailwind + Recharts（簡易UI）
- `backend/`  … FastAPI（`/hachimura/games`, `/hachimura/season-avg`, `/health`）
- `backend/data/games_2024_25.json` … サンプルのゲームログ（3試合）

## エンドポイント
- `GET /health` … ヘルスチェック
- `GET /hachimura/games?limit=20` … ゲームログ（TS%/eFG%を各試合に付与）
- `GET /hachimura/season-avg?season=2024-25` … シーズン集計（TS/eFGは合算から計算）

## 変更ポイント
- データ取得元を無料APIやGitHub Actions生成JSONに差し替える場合は、
  `backend/app/main.py` の `load_games()` を修正してください。
- CORSは `http://localhost:3000` を許可しています。必要に応じて調整。

## メモ
- 本テンプレは *開発用* 設定です（Next.jsは`dev`起動）。本番用は `npm run build && next start` や
  Nginx などの静的配信 + SSR/Edgeの構成に置き換えてください。
