from sqlalchemy import Column, Integer, String, Float
from app.db.session import Base


class Team(Base):
    __tablename__ = "teams"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    budget_remaining = Column(Float, nullable=False)
    color = Column(String)
    pin_hash = Column(String, nullable=False)
