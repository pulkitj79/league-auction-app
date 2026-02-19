from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.services.admin_service import AdminService
from app.core.dependencies import require_role
from app.core.constants import UserRole


router = APIRouter(prefix="/api/admin", tags=["Admin"])


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
