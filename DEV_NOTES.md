# Developer Notes

## Local Development

## Run

```bash
uvicorn main:app --reload
```

Server defaults to `http://127.0.0.1:8000`.

## Key URLs

- `/` health endpoint
- `/auctioneer` auctioneer UI
- `/bidder` bidder UI
- `/projector` projector UI
- `/docs` FastAPI Swagger docs

## Authentication Flow

- Auctioneer login: `POST /api/auth/login/auctioneer?secret_key=...`
- Bidder login: `POST /api/auth/login/bidder?team_name=...&pin=...`
- Tokens are stored in `sessions` table and sent as `Authorization: Bearer <token>`.

## Data Loading Options

### Admin load (uses repo `data/`)

`POST /api/admin/load-from-root` (auctioneer role required)

- Clears existing teams, players, and pools.
- Hashes team PINs using bcrypt.
- Recreates pools from player CSV ordering.

### Upload APIs

- `POST /api/import/teams`
- `POST /api/import/players`

Enabled via `features.enable_csv_upload` in `config.yaml`.

## Auction State Model (important)

`auction_state` is a singleton-like mutable row holding live state:

- `current_player_id`
- `current_highest_bid`
- `current_highest_team_id`
- `status`
- `bidding_end_time`

Most auction actions mutate this row, then broadcast an event.

## Realtime Events

WebSocket endpoint: `/ws`

Current event set in code:

- `PLAYER_LOADED`
- `BIDDING_STARTED`
- `NEW_BID`
- `COUNTDOWN_TICK`
- `COUNTDOWN_CANCELLED`
- `BIDDING_EXTENDED`
- `BIDDING_CLOSED`

## Known Implementation Gaps / Risks

- `auction-engine.js` expects fields (`status`, `teams`) that do not exactly match `/full-state` response (`auction_status`, `leaderboard`). UI still receives events, but initial state mapping may drift.
- `config.yaml` auction keys differ from some keys read in `AuctionService` (`default_extension_seconds`, `countdown_seconds`), causing fallback defaults to be used.
- `Bid` model exists but accepted bids are not persisted in `bids` table.
- WebSocket manager stores connections in-memory; no distributed fanout.
- `ConnectionManager.disconnect` assumes connection exists and may throw if called twice.

## Recommended Dev Improvements

1. Align `/full-state` response contract with frontend expectations (or update frontend mapping).
2. Normalize auction config key names across config and service.
3. Persist bid audit trail to `bids` table.
4. Add unit tests for auction transitions and auth guards.
5. Add structured logging around state changes and failed bids.

## Handy Commands

```bash
# syntax check
python -m compileall app main.py

# run app
uvicorn main:app --reload
```
