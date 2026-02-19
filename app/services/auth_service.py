import uuid
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from passlib.context import CryptContext

from app.models.team import Team
from app.models.session import Session as UserSession
from app.core.constants import UserRole, Defaults


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class AuthService:

    def __init__(self, db: Session):
        self.db = db

    # ---------------------------------------
    # TEAM LOGIN
    # ---------------------------------------
    def login_bidder(self, team_name: str, pin: str):

        team = self.db.query(Team).filter(
            Team.name == team_name
        ).first()

        if not team:
            raise Exception("Invalid team")

        if not pwd_context.verify(pin, team.pin_hash):
            raise Exception("Invalid PIN")

        return self._create_session(UserRole.BIDDER.value, team.id)

    # ---------------------------------------
    # AUCTIONEER LOGIN
    # ---------------------------------------
    def login_auctioneer(self, secret_key: str, configured_key: str):

        if secret_key != configured_key:
            raise Exception("Invalid secret key")

        return self._create_session(UserRole.AUCTIONEER.value, None)

    # ---------------------------------------
    # CREATE SESSION
    # ---------------------------------------
    def _create_session(self, role: str, team_id: int):

        token = str(uuid.uuid4())

        expires_at = datetime.utcnow() + timedelta(
            hours=Defaults.SESSION_EXPIRY_HOURS
        )

        session = UserSession(
            token=token,
            role=role,
            team_id=team_id,
            expires_at=expires_at
        )

        self.db.add(session)
        self.db.commit()

        return {
            "access_token": token,
            "role": role
        }

    # ---------------------------------------
    # VALIDATE TOKEN
    # ---------------------------------------
    def validate_token(self, token: str):

        session = self.db.query(UserSession).filter(
            UserSession.token == token,
            UserSession.is_active == True
        ).first()

        if not session:
            raise Exception("Invalid session")

        if session.expires_at < datetime.utcnow():
            raise Exception("Session expired")

        return session
