from sqlalchemy import Column, Integer, String, Boolean, Float, JSON
from app.db.session import Base


class AuctionConfig(Base):
    __tablename__ = "auction_config"

    id = Column(Integer, primary_key=True, index=True)

    # Purse configuration
    purse_type = Column(String, default="CURRENCY")  # CURRENCY or POINTS
    initial_purse_value = Column(Float, default=10000000)

    # Increment configuration
    increment_mode = Column(String, default="OPEN")  
    # OPEN, FIXED, TIERED

    fixed_increment_value = Column(Float, nullable=True)

    tier_rules = Column(JSON, nullable=True)
    # Example:
    # [
    #   {"min": 0, "max": 1000000, "step": 50000},
    #   {"min": 1000000, "max": 5000000, "step": 100000},
    #   {"min": 5000000, "max": null, "step": 500000}
    # ]

    # Countdown behavior
    auto_reset_on_new_bid = Column(Boolean, default=False)

    # UI configuration
    allow_manual_input = Column(Boolean, default=True)
    number_of_increment_buttons = Column(Integer, default=0)

     # 🔥 New rule-driven engine config
    
    rule_config = Column(JSON, nullable=False, default=dict)
    rule_config={
        "increment": {
            "mode": "FIXED_MULTI",
            "values": [2, 3]
        }
    }