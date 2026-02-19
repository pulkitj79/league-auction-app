# Architecture

## High-Level Overview

The system is a monolithic FastAPI app with:

- REST APIs for auth, import, admin, and auction actions.
- A shared SQLite database accessed via SQLAlchemy.
- A WebSocket broadcast channel for real-time UI updates.
- Server-rendered HTML pages (Jinja templates) that load a shared client-side auction engine.

```text
Browser UIs (auctioneer / bidder / projector)
          | REST + WebSocket
          v
       FastAPI app
   (routers -> services)
          |
          v
     SQLAlchemy ORM
          |
          v
        SQLite
```

## Runtime Components

## 1. App bootstrap (`main.py`)

- Instantiates FastAPI app.
- Creates DB tables via `Base.metadata.create_all`.
- Ensures a default `auction_config` row exists.
- Registers API routers.
- Mounts static files and template routes.
- Hosts WebSocket endpoint `/ws` that registers clients in a global connection manager.

## 2. Configuration (`app/core/settings.py`, `config.yaml`)

- `Settings` reads `config.yaml` once at startup.
- Exposes grouped config (`database`, `auction`, `features`, `security`).
- Database URL is consumed by DB session setup.

## 3. Persistence (`app/db/session.py`, `app/models/*`)

Primary tables:

- `teams`: team identity, budget, color, PIN hash.
- `players`: player attributes, auction status, sold info, pool reference.
- `pools`: sequencing groups for player loading.
- `auction_state`: singleton-like row for current live auction state.
- `sessions`: login sessions and role tokens.
- `auction_config`: future-facing runtime config model.
- `bids`: bid model exists but is not actively persisted by service flow.

## 4. Auth and authorization

- `AuthService` validates bidder PIN (bcrypt hash) and auctioneer secret.
- Successful login creates a token row in `sessions`.
- `get_current_session` dependency validates bearer token and expiry.
- `require_role` enforces endpoint-level role access.

## 5. Auction domain logic (`AuctionService`)

Core workflow:

1. **Load next player** using active pool ordering.
2. **Start bidding** and initialize highest bid from base price.
3. **Accept bids** with validation (status, amount, budget).
4. **Start countdown** and run async timer loop.
5. **Cancel/extend countdown** as needed.
6. **Force close** to mark SOLD/UNSOLD and update team budget.

`auction_state` acts as the source of truth for current player, price, leading team, status, and countdown end-time.

## 6. Realtime transport (`app/websocket/manager.py`)

- In-memory list of active WebSocket connections.
- `broadcast(message)` sends JSON events to all connected clients.
- Auction service emits domain events like `PLAYER_LOADED`, `NEW_BID`, and `COUNTDOWN_TICK`.

## 7. Frontend behavior

- Three templates load shared `static/js/auction-engine.js`.
- JS fetches `/api/auction/full-state` and listens on `/ws`.
- UI state is rendered from snapshot + event stream.
- Auctioneer and bidder pages additionally perform login + authorized actions.

## API Surface by Responsibility

- `app/routers/auth.py`: login endpoints.
- `app/routers/auction.py`: live auction controls + bidding + state snapshot.
- `app/routers/import_data.py`: file-based import endpoints (feature-flagged).
- `app/routers/admin.py`: root `data/` bulk load endpoint.

## Design Constraints and Trade-offs

- **SQLite + WAL mode** keeps setup simple, but limits horizontal scaling.
- **In-memory WebSocket connection registry** is simple, but single-process scoped.
- **Global countdown task variable** is straightforward, but not multi-worker safe.
- **Mostly synchronous DB operations** inside async endpoints are acceptable for small workloads.

## Suggested Future Evolutions

- Persist bid history to `bids` table on each accepted bid.
- Add robust exception mapping (domain errors -> structured HTTP responses).
- Replace in-memory broadcast with Redis pub/sub for multi-instance deployments.
- Introduce migrations (Alembic) instead of startup `create_all`.
- Add automated tests around auction state transitions.
