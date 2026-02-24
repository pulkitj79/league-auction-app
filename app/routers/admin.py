from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.services.admin_service import AdminService
from app.core.dependencies import require_role
from app.core.constants import UserRole
from app.services.team_service import TeamService
from fastapi import Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from app.services.player_service import PlayerService
from app.services.pool_service import PoolService   
from app.services.config_service import ConfigService


router = APIRouter(prefix="/api/admin", tags=["Admin"])
templates = Jinja2Templates(directory="templates")


@router.post("/load-from-root")
def load_from_root(
    db: Session = Depends(get_db),
    session=Depends(require_role(UserRole.AUCTIONEER.value))
):
    service = AdminService(db)

    try:
        return service.load_from_root()
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/teams-page", response_class=HTMLResponse)
def teams_page(
    request: Request,
    db: Session = Depends(get_db),
    #session=Depends(require_role(UserRole.AUCTIONEER.value))
):
    service = TeamService(db)
    teams = service.get_all()

    return templates.TemplateResponse(
        "admin_teams.html",
        {"request": request, "teams": teams}
    )

@router.get("/teams")
def get_teams(
    db: Session = Depends(get_db),
    session=Depends(require_role(UserRole.AUCTIONEER.value))
):
    service = TeamService(db)
    return service.get_all()


@router.post("/teams")
def create_team(
    name: str,
    budget: float,
    pin: str,
    color: str = None,
    db: Session = Depends(get_db),
    session=Depends(require_role(UserRole.AUCTIONEER.value))
):
    service = TeamService(db)
    return service.create(name, budget, pin, color)



@router.put("/teams/{team_id}")
def update_team(
    team_id: int,
    name: str,
    budget: float,
    db: Session = Depends(get_db),
    session=Depends(require_role(UserRole.AUCTIONEER.value))
):
    service = TeamService(db)
    return service.update(team_id, name, budget)


@router.delete("/teams/{team_id}")
def delete_team(
    team_id: int,
    db: Session = Depends(get_db),
    session=Depends(require_role(UserRole.AUCTIONEER.value))
):
    service = TeamService(db)
    return service.delete(team_id)

@router.get("/players-page", response_class=HTMLResponse)
def players_page(
    request: Request,
    db: Session = Depends(get_db)
):
    service = PlayerService(db)
    players = service.get_all()
    pools = service.get_pools()

    return templates.TemplateResponse(
        "admin_players.html",
        {
            "request": request,
            "players": players,
            "pools": pools
        }
    )

@router.get("/players")
def get_players(
    db: Session = Depends(get_db),
    session=Depends(require_role(UserRole.AUCTIONEER.value))
):
    service = PlayerService(db)
    return service.get_all()


@router.post("/players")
def create_player(
    name: str,
    base_price: float,
    pool_id: int = None,
    db: Session = Depends(get_db),
    session=Depends(require_role(UserRole.AUCTIONEER.value))
):
    service = PlayerService(db)
    return service.create(name, base_price, pool_id)


@router.delete("/players/{player_id}")
def delete_player(
    player_id: int,
    db: Session = Depends(get_db),
    session=Depends(require_role(UserRole.AUCTIONEER.value))
):
    service = PlayerService(db)
    return service.delete(player_id)

@router.get("/pools-page", response_class=HTMLResponse)
def pools_page(
    request: Request,
    db: Session = Depends(get_db)
):
    service = PoolService(db)
    pools = service.get_all()

    return templates.TemplateResponse(
        "admin_pools.html",
        {
            "request": request,
            "pools": pools
        }
    )

@router.post("/pools")
def create_pool(
    name: str,
    sequence_order: int,
    is_active: bool = True,
    db: Session = Depends(get_db),
    session=Depends(require_role(UserRole.AUCTIONEER.value))
):
    service = PoolService(db)
    return service.create(name, sequence_order, is_active)


@router.delete("/pools/{pool_id}")
def delete_pool(
    pool_id: int,
    db: Session = Depends(get_db),
    session=Depends(require_role(UserRole.AUCTIONEER.value))
):
    service = PoolService(db)
    return service.delete(pool_id)


@router.post("/pools/{pool_id}/toggle")
def toggle_pool(
    pool_id: int,
    db: Session = Depends(get_db),
    session=Depends(require_role(UserRole.AUCTIONEER.value))
):
    service = PoolService(db)
    return service.toggle_active(pool_id)

@router.get("/config-page", response_class=HTMLResponse)
def config_page(
    request: Request,
    db: Session = Depends(get_db)
):
    service = ConfigService(db)
    config = service.get()

    return templates.TemplateResponse(
        "admin_config.html",
        {
            "request": request,
            "config": config
        }
    )

@router.post("/config")
def update_config(
    purse_type: str,
    initial_purse_value: float,
    increment_mode: str,
    fixed_increment_value: float = None,
    tier_rules: str = None,
    auto_reset_on_new_bid: bool = True,
    allow_manual_input: bool = True,
    number_of_increment_buttons: int = 3,
    db: Session = Depends(get_db),
    session=Depends(require_role(UserRole.AUCTIONEER.value))
):
    service = ConfigService(db)

    return service.update(
        purse_type=purse_type,
        initial_purse_value=initial_purse_value,
        increment_mode=increment_mode,
        fixed_increment_value=fixed_increment_value,
        tier_rules=tier_rules,
        auto_reset_on_new_bid=auto_reset_on_new_bid,
        allow_manual_input=allow_manual_input,
        number_of_increment_buttons=number_of_increment_buttons
    )