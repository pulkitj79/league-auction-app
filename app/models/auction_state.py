from sqlalchemy import Column, Integer, Float, String, DateTime
from sqlalchemy.sql import func
from app.db.session import Base
from app.core.constants import AuctionStatus


class AuctionState(Base):
    __tablename__ = "auction_state"

    id = Column(Integer, primary_key=True, index=True)
    current_player_id = Column(Integer)
    current_highest_bid = Column(Float, default=0)
    current_highest_team_id = Column(Integer)
    status = Column(String, default=AuctionStatus.IDLE.value)
    bidding_end_time = Column(DateTime(timezone=True))
    last_updated = Column(DateTime(timezone=True),
                          server_default=func.now(),
                          onupdate=func.now())
