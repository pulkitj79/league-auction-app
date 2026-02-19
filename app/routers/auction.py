from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.services.auction_service import AuctionService
from app.models.player import Player
from app.models.team import Team
from app.models.auction_state import AuctionState
from app.models.pool import Pool

from app.core.dependencies import require_role, get_current_session
from app.core.constants import UserRole


router = APIRouter(prefix="/api/auction", tags=["Auction"])


# -------------------------------------------------
# LOAD NEXT PLAYER (Auctioneer Only)
# -------------------------------------------------
@router.post("/load-next")
async def load_next(
    db: Session = Depends(get_db),
    session=Depends(require_role(UserRole.AUCTIONEER.value))
):
    service = AuctionService(db)
    return await service.load_next_player()


# -------------------------------------------------
# START BIDDING (Auctioneer Only)
# -------------------------------------------------
@router.post("/start")
async def start(
    db: Session = Depends(get_db),
    session=Depends(require_role(UserRole.AUCTIONEER.value))
):
    service = AuctionService(db)
    return await service.start_bidding()


# -------------------------------------------------
# EXTEND (Auctioneer Only)
# -------------------------------------------------
@router.post("/extend")
async def extend(
    db: Session = Depends(get_db),
    session=Depends(require_role(UserRole.AUCTIONEER.value))
):
    service = AuctionService(db)
    return await service.extend_bidding()


# -------------------------------------------------
# START COUNTDOWN (Auctioneer Only)
# -------------------------------------------------
@router.post("/start-countdown")
async def start_countdown(
    db: Session = Depends(get_db),
    session=Depends(require_role(UserRole.AUCTIONEER.value))
):
    service = AuctionService(db)
    return await service.start_countdown()


# -------------------------------------------------
# CANCEL COUNTDOWN (Auctioneer Only)
# -------------------------------------------------
@router.post("/cancel-countdown")
async def cancel_countdown(
    db: Session = Depends(get_db),
    session=Depends(require_role(UserRole.AUCTIONEER.value))
):
    service = AuctionService(db)
    return await service.cancel_countdown()


# -------------------------------------------------
# FORCE CLOSE (Auctioneer Only)
# -------------------------------------------------
@router.post("/force-close")
async def force_close(
    db: Session = Depends(get_db),
    session=Depends(require_role(UserRole.AUCTIONEER.value))
):
    service = AuctionService(db)
    return await service.force_close()


# -------------------------------------------------
# BID (Bidder Only)
# -------------------------------------------------
@router.post("/bid")
async def place_bid(
    amount: float,
    db: Session = Depends(get_db),
    session=Depends(require_role(UserRole.BIDDER.value))
):
    service = AuctionService(db)

    # Team ID comes from session now
    return await service.place_bid(session.team_id, amount)


# -------------------------------------------------
# FULL STATE (Broadcast Ready)
# -------------------------------------------------
@router.get("/full-state")
def full_state(db: Session = Depends(get_db)):

    state = db.query(AuctionState).first()

    if not state:
        return {"message": "Auction not initialized"}

    players = db.query(Player).all()
    teams = db.query(Team).all()

    total_players = len(players)
    sold_players = [p for p in players if p.status == "SOLD"]
    unsold_players = [p for p in players if p.status == "UNSOLD"]
    available_players = [p for p in players if p.status == "AVAILABLE"]

    # Current player details
    current_player = None
    if state.current_player_id:
        player_obj = db.query(Player).filter(
            Player.id == state.current_player_id
        ).first()

        if player_obj:
            current_player = {
                "id": player_obj.id,
                "name": player_obj.name,
                "role": player_obj.role,
                "base_price": player_obj.base_price,
                "status": player_obj.status
            }

    # Leaderboard calculation
    leaderboard = []
    for team in teams:
        won_players = [p for p in sold_players if p.sold_to_team == team.id]
        total_spent = sum(p.sold_price for p in won_players if p.sold_price)

        leaderboard.append({
            "id": team.id,
            "name": team.name,
            "color": team.color,
            "budget_remaining": team.budget_remaining,
            "players_won": len(won_players),
            "total_spent": total_spent
        })

    # Sort by total spent descending
    leaderboard.sort(key=lambda x: x["total_spent"], reverse=True)

    highest_team = None
    if state.current_highest_team_id:
        team_obj = db.query(Team).filter(
            Team.id == state.current_highest_team_id
        ).first()

        if team_obj:
            highest_team = {
                "id": team_obj.id,
                "name": team_obj.name,
                "color": team_obj.color
            }

    return {
        "auction_status": state.status,
        "current_player": current_player,
        "current_highest_bid": state.current_highest_bid,
        "current_highest_team": highest_team,
        "total_players": total_players,
        "sold_count": len(sold_players),
        "unsold_count": len(unsold_players),
        "available_count": len(available_players),
        "leaderboard": leaderboard
    }
