import asyncio
from datetime import datetime, timedelta
from typing import Optional

from sqlalchemy.orm import Session

from app.models.player import Player
from app.models.team import Team
from app.models.pool import Pool
from app.models.auction_state import AuctionState
from app.websocket.manager import manager
from app.core.constants import AuctionEvent, AuctionStatus, Defaults
from app.core.settings import settings


_countdown_task: Optional[asyncio.Task] = None


class AuctionService:
    def __init__(self, db: Session):
        self.db = db

    # ------------------------------------------------
    # Ensure auction state row exists
    # ------------------------------------------------
    def _get_or_create_state(self) -> AuctionState:
        state = self.db.query(AuctionState).first()
        if not state:
            state = AuctionState(
                current_player_id=None,
                current_highest_bid=0,
                current_highest_team_id=None,
                status=AuctionStatus.IDLE.value,
                bidding_end_time=None,
            )
            self.db.add(state)
            self.db.commit()
            self.db.refresh(state)
        return state

    # ------------------------------------------------
    # Pool-based next player selection
    # ------------------------------------------------
    def _find_next_player(self) -> Optional[Player]:
        pools = (
            self.db.query(Pool)
            .filter(Pool.is_active == True)
            .order_by(Pool.sequence_order)
            .all()
        )

        for pool in pools:
            player = (
                self.db.query(Player)
                .filter(
                    Player.pool_id == pool.id,
                    Player.status == "AVAILABLE"
                )
                .order_by(Player.id)
                .first()
            )
            if player:
                return player

        return (
            self.db.query(Player)
            .filter(Player.status == "AVAILABLE")
            .order_by(Player.id)
            .first()
        )

    # ------------------------------------------------
    # LOAD NEXT PLAYER
    # ------------------------------------------------
    async def load_next_player(self):
        state = self._get_or_create_state()

        if state.status == AuctionStatus.ENDING_COUNTDOWN.value:
            raise Exception("Cannot load next while countdown running")

        player = self._find_next_player()
        if not player:
            raise Exception("No available players to load")

        state.current_player_id = player.id
        state.current_highest_bid = player.base_price or 0
        state.current_highest_team_id = None
        state.status = AuctionStatus.IDLE.value
        state.bidding_end_time = None

        self.db.commit()

        await manager.broadcast({
            "event": AuctionEvent.PLAYER_LOADED.value,
            "player_id": player.id,
            "player_name": player.name,
        })

        return {
            "status": "player_loaded",
            "player_id": player.id,
            "player_name": player.name,
        }

    # ------------------------------------------------
    # START BIDDING
    # ------------------------------------------------
    async def start_bidding(self):
        state = self._get_or_create_state()

        if not state.current_player_id:
            raise Exception("No player loaded")

        state.status = AuctionStatus.BIDDING_OPEN.value

        player = self.db.query(Player).filter(
            Player.id == state.current_player_id
        ).first()

        if player and (
            state.current_highest_bid is None
            or state.current_highest_bid < (player.base_price or 0)
        ):
            state.current_highest_bid = player.base_price or 0
            state.current_highest_team_id = None

        state.bidding_end_time = None
        self.db.commit()

        await manager.broadcast({
            "event": AuctionEvent.BIDDING_STARTED.value
        })

        return {"status": "bidding_started"}

    # ------------------------------------------------
    # PLACE BID
    # ------------------------------------------------
    async def place_bid(self, team_id: int, amount: float):

        if team_id is None:
            raise Exception("Invalid team session")

        state = self._get_or_create_state()

        if state.status != AuctionStatus.BIDDING_OPEN.value:
            raise Exception("Bidding not open")

        if not state.current_player_id:
            raise Exception("No player loaded")

        team = self.db.query(Team).filter(
            Team.id == team_id
        ).first()

        if not team:
            raise Exception("Team not found")

        player = self.db.query(Player).filter(
            Player.id == state.current_player_id
        ).first()

        if not player:
            raise Exception("Player not found")

        try:
            amount_val = float(amount)
        except Exception:
            raise Exception("Invalid amount")

        if amount_val <= (state.current_highest_bid or 0):
            raise Exception("Bid too low")

        if amount_val > team.budget_remaining:
            raise Exception("Insufficient budget")

        state.current_highest_bid = amount_val
        state.current_highest_team_id = team.id

        self.db.commit()

        await manager.broadcast({
            "event": AuctionEvent.NEW_BID.value,
            "amount": amount_val,
            "team_id": team.id,
            "team_name": team.name
        })

        return {
            "status": "bid_accepted",
            "amount": amount_val,
            "team_id": team.id,
            "team_name": team.name
        }

    # ------------------------------------------------
    # EXTEND BIDDING
    # ------------------------------------------------
    async def extend_bidding(self, extra_seconds: Optional[int] = None):
        state = self._get_or_create_state()

        if state.status not in (
            AuctionStatus.BIDDING_OPEN.value,
            AuctionStatus.ENDING_COUNTDOWN.value,
        ):
            raise Exception("Bidding must be open to extend")

        try:
            default_ext = int(
                settings.auction.get("default_extension_seconds", 60)
            )
        except Exception:
            default_ext = 60

        extra = extra_seconds if extra_seconds is not None else default_ext

        if state.bidding_end_time:
            state.bidding_end_time += timedelta(seconds=extra)
        else:
            state.bidding_end_time = datetime.utcnow() + timedelta(seconds=extra)

        state.status = AuctionStatus.BIDDING_OPEN.value
        self.db.commit()

        await manager.broadcast({
            "event": AuctionEvent.BIDDING_EXTENDED.value,
            "new_end_time": state.bidding_end_time.isoformat()
        })

        return {
            "status": "extended",
            "new_end_time": state.bidding_end_time.isoformat()
        }

    # ------------------------------------------------
    # START COUNTDOWN
    # ------------------------------------------------
    async def start_countdown(self, countdown_seconds: Optional[int] = None):
        global _countdown_task

        state = self._get_or_create_state()

        if state.status != AuctionStatus.BIDDING_OPEN.value:
            raise Exception("Bidding must be open to start countdown")

        try:
            default_seconds = int(
                settings.auction.get("countdown_seconds", 10)
            )
        except Exception:
            default_seconds = 10

        seconds = countdown_seconds if countdown_seconds else default_seconds

        state.bidding_end_time = datetime.utcnow() + timedelta(seconds=seconds)
        state.status = AuctionStatus.ENDING_COUNTDOWN.value
        self.db.commit()

        if _countdown_task and not _countdown_task.done():
            _countdown_task.cancel()

        _countdown_task = asyncio.create_task(self._countdown_loop())

        return {"status": "countdown_started", "seconds": seconds}

    # ------------------------------------------------
    # CANCEL COUNTDOWN
    # ------------------------------------------------
    async def cancel_countdown(self):
        global _countdown_task

        state = self._get_or_create_state()

        if _countdown_task and not _countdown_task.done():
            _countdown_task.cancel()

        state.bidding_end_time = None
        state.status = AuctionStatus.BIDDING_OPEN.value
        self.db.commit()

        await manager.broadcast({
            "event": AuctionEvent.COUNTDOWN_CANCELLED.value
        })

        return {"status": "countdown_cancelled"}

    # ------------------------------------------------
    # FORCE CLOSE
    # ------------------------------------------------
    async def force_close(self):
        state = self._get_or_create_state()

        if not state.current_player_id:
            raise Exception("No player loaded")

        winner_id = state.current_highest_team_id
        amount = state.current_highest_bid

        player = self.db.query(Player).filter(
            Player.id == state.current_player_id
        ).first()

        if winner_id:
            team = self.db.query(Team).filter(
                Team.id == winner_id
            ).first()

            team.budget_remaining -= amount
            player.sold_price = amount
            player.sold_to_team = team.id
            player.status = "SOLD"

        else:
            player.status = "UNSOLD"

        state.current_player_id = None
        state.current_highest_bid = 0
        state.current_highest_team_id = None
        state.status = AuctionStatus.IDLE.value
        state.bidding_end_time = None

        self.db.commit()

        await manager.broadcast({
            "event": AuctionEvent.BIDDING_CLOSED.value,
            "winner_team_id": winner_id
        })

        return {"status": "closed"}

    # ------------------------------------------------
    # COUNTDOWN LOOP
    # ------------------------------------------------
    async def _countdown_loop(self):
        global _countdown_task

        try:
            while True:
                state = self._get_or_create_state()

                if not state.bidding_end_time:
                    return

                remaining = int(
                    (state.bidding_end_time - datetime.utcnow())
                    .total_seconds()
                )

                if remaining <= 0:
                    await self.force_close()
                    return

                await manager.broadcast({
                    "event": AuctionEvent.COUNTDOWN_TICK.value,
                    "seconds": remaining
                })

                await asyncio.sleep(1)

        except asyncio.CancelledError:
            return
        finally:
            _countdown_task = None
