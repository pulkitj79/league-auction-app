from sqlalchemy.orm import Session
from app.models.auction_config import AuctionConfig


class ConfigService:

    def __init__(self, db: Session):
        self.db = db

    def get(self):
        config = self.db.query(AuctionConfig).first()
        if not config:
            config = AuctionConfig()
            self.db.add(config)
            self.db.commit()
            self.db.refresh(config)
        return config

    def update(self, **kwargs):
        config = self.get()

        for key, value in kwargs.items():
            if hasattr(config, key):
                setattr(config, key, value)

        self.db.commit()
        self.db.refresh(config)
        return config