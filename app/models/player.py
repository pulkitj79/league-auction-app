from sqlalchemy import Column, Integer, String, Float, ForeignKey
from app.db.session import Base
from app.core.constants import PlayerStatus


class Player(Base):
    __tablename__ = "players"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    role = Column(String)
    base_price = Column(Float, nullable=False)
    sold_price = Column(Float)
    sold_to_team = Column(Integer, ForeignKey("teams.id"))
    status = Column(String, default=PlayerStatus.AVAILABLE.value)
    pool_id = Column(Integer, ForeignKey("pools.id"))
