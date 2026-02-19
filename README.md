# League Auction App

A real-time auction platform for running team-based player auctions. The app provides three browser experiences:

- **Auctioneer console** (`/auctioneer`) for controlling auction flow.
- **Bidder console** (`/bidder`) for team logins and live bidding.
- **Projector view** (`/projector`) for display-only live updates.

The backend is built with **FastAPI**, **SQLAlchemy**, and **WebSockets** over a SQLite database.

## Features

- Session-based auth for auctioneer and bidders.
- CSV/Excel player and team import endpoints.
- Admin one-click import from `data/` folder.
- Pool-based player sequencing.
- Live bid updates over WebSocket broadcast.
- Countdown, extension, cancellation, and force-close controls.

## Quick Start

## 1) Prerequisites

- Python 3.10+
- pip

## 2) Install dependencies

```bash
pip install -r requirements.txt
```

## 3) Configure app

Edit `config.yaml` for:

- Database URL (`database.url`)
- Auction options (`auction.*`)
- Feature toggles (`features.*`)
- Auctioneer secret (`security.auctioneer_key`)

## 4) Run server

```bash
uvicorn main:app --reload
```

App routes:

- Health: `GET /`
- Auctioneer UI: `GET /auctioneer`
- Bidder UI: `GET /bidder`
- Projector UI: `GET /projector`

## 5) Load initial data

Option A (recommended for local demo):

```bash
# first, login as auctioneer in /auctioneer to get a token
curl -X POST "http://localhost:8000/api/admin/load-from-root" \
  -H "Authorization: Bearer <auctioneer_token>"
```

Option B: import files via API endpoints:

- `POST /api/import/teams`
- `POST /api/import/players`

## Common API Endpoints

### Authentication

- `POST /api/auth/login/auctioneer?secret_key=...`
- `POST /api/auth/login/bidder?team_name=...&pin=...`

### Auction control (auctioneer only)

- `POST /api/auction/load-next`
- `POST /api/auction/start`
- `POST /api/auction/start-countdown`
- `POST /api/auction/extend`
- `POST /api/auction/cancel-countdown`
- `POST /api/auction/force-close`

### Bidding

- `POST /api/auction/bid?amount=...` (bidder only)

### State snapshot

- `GET /api/auction/full-state`

## Data Expectations

`data/teams.csv` must contain columns:

- `name`
- `budget_remaining`
- `color`
- `pin`

`data/players.csv` must contain columns:

- `name`
- `role`
- `base_price`
- `pool`

## Repository Layout

```text
app/
  core/           # constants, settings loader, auth dependencies
  db/             # SQLAlchemy engine/session
  models/         # ORM tables
  routers/        # API route groups
  services/       # business logic
  utils/          # import helpers
  websocket/      # connection manager
static/
  css/            # styles
  js/             # auction realtime client
templates/        # auctioneer/bidder/projector pages
data/             # sample CSV files
```

## Notes

- Database tables are created automatically at startup.
- A default `auction_config` row is also auto-created on startup.
- WebSocket endpoint is `/ws` and broadcasts auction events to all connected clients.
