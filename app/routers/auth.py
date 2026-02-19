from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.services.auth_service import AuthService
from app.core.settings import settings


router = APIRouter(prefix="/api/auth", tags=["Authentication"])


# -----------------------------------------
# BIDDER LOGIN
# -----------------------------------------
@router.post("/login/bidder")
def login_bidder(team_name: str, pin: str, db: Session = Depends(get_db)):

    auth_service = AuthService(db)

    try:
        return auth_service.login_bidder(team_name, pin)
    except Exception as e:
        raise HTTPException(status_code=401, detail=str(e))


# -----------------------------------------
# AUCTIONEER LOGIN
# -----------------------------------------
@router.post("/login/auctioneer")
def login_auctioneer(secret_key: str, db: Session = Depends(get_db)):

    auth_service = AuthService(db)

    configured_key = settings.security.get("auctioneer_key")

    try:
        return auth_service.login_auctioneer(secret_key, configured_key)
    except Exception as e:
        raise HTTPException(status_code=401, detail=str(e))
