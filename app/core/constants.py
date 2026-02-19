from enum import Enum


# ----------------------------------------
# Roles
# ----------------------------------------
class UserRole(str, Enum):
    AUCTIONEER = "AUCTIONEER"
    BIDDER = "BIDDER"
    PROJECTOR = "PROJECTOR"


# ----------------------------------------
# Player Status
# ----------------------------------------
class PlayerStatus(str, Enum):
    AVAILABLE = "AVAILABLE"
    SOLD = "SOLD"
    UNSOLD = "UNSOLD"


# ----------------------------------------
# Auction Status
# ----------------------------------------
class AuctionStatus(str, Enum):
    IDLE = "IDLE"
    BIDDING_OPEN = "BIDDING_OPEN"
    BIDDING_PAUSED = "BIDDING_PAUSED"
    ENDING_COUNTDOWN = "ENDING_COUNTDOWN"
    CLOSED = "CLOSED"


# ----------------------------------------
# System Pools
# ----------------------------------------
class SystemPools:
    UNSOLD_POOL = "UNSOLD_POOL"


# ----------------------------------------
# Auction Events
# ----------------------------------------
class AuctionEvent(str, Enum):
    PLAYER_LOADED = "PLAYER_LOADED"
    BIDDING_STARTED = "BIDDING_STARTED"
    BIDDING_PAUSED = "BIDDING_PAUSED"
    NEW_BID = "NEW_BID"
    COUNTDOWN_TICK = "COUNTDOWN_TICK"
    COUNTDOWN_CANCELLED = "COUNTDOWN_CANCELLED"
    BIDDING_CLOSED = "BIDDING_CLOSED"
    BIDDING_EXTENDED = "BIDDING_EXTENDED"


# ----------------------------------------
# Defaults
# ----------------------------------------
class Defaults:
    TEAM_COLOR = "blue"
    UNSOLD_POOL_FALLBACK_SEQUENCE = 10000
    SESSION_EXPIRY_HOURS = 6
