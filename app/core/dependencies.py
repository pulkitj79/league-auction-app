from fastapi import Header, HTTPException, Depends
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.services.auth_service import AuthService
from app.core.constants import UserRole


def get_current_session(
    authorization: str = Header(None),
    db: Session = Depends(get_db)
):

    if not authorization:
        raise HTTPException(status_code=401, detail="Authorization header missing")

    token = authorization.replace("Bearer ", "")

    auth_service = AuthService(db)

    try:
        return auth_service.validate_token(token)
    except Exception as e:
        raise HTTPException(status_code=401, detail=str(e))


def require_role(required_role: str):
    def role_checker(session=Depends(get_current_session)):
        if session.role != required_role:
            raise HTTPException(status_code=403, detail="Forbidden")
        return session
    return role_checker
