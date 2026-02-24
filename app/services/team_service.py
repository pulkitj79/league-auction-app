from sqlalchemy.orm import Session
from app.models.team import Team
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"],deprecated="auto")



class TeamService:

    def __init__(self, db: Session):
        self.db = db

    def get_all(self):
        return self.db.query(Team).order_by(Team.id).all()

    def create(self, name: str, budget: float, pin: str, color: str = None):
        if not pin:
            raise Exception("PIN required")
        
        pin_hash = pwd_context.hash(pin)

        team = Team(
            name=name,
            budget_remaining=budget,
            color=color,
            pin_hash=pin_hash
        )

        self.db.add(team)
        self.db.commit()
        self.db.refresh(team)
        return team


    def update(self, team_id: int, name: str, budget: float):
        team = self.db.query(Team).filter(Team.id == team_id).first()
        if not team:
            raise Exception("Team not found")

        team.name = name
        team.budget_remaining = budget

        self.db.commit()
        return team

    def delete(self, team_id: int):
        team = self.db.query(Team).filter(Team.id == team_id).first()
        if not team:
            raise Exception("Team not found")

        self.db.delete(team)
        self.db.commit()
        return {"status": "deleted"}
