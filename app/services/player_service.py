from sqlalchemy.orm import Session
from app.models.player import Player
from app.models.pool import Pool


class PlayerService:

    def __init__(self, db: Session):
        self.db = db

    def get_all(self):
        return self.db.query(Player).order_by(Player.id).all()

    def get_pools(self):
        return self.db.query(Pool).order_by(Pool.sequence_order).all()

    def create(self, name: str, base_price: float, pool_id: int = None):
        player = Player(
            name=name,
            base_price=base_price,
            pool_id=pool_id,
            status="AVAILABLE",
            sold_price=None,
            sold_to_team=None
        )

        self.db.add(player)
        self.db.commit()
        self.db.refresh(player)
        return player

    def delete(self, player_id: int):
        player = self.db.query(Player).filter(Player.id == player_id).first()

        if not player:
            raise Exception("Player not found")

        if player.status != "AVAILABLE":
            raise Exception("Cannot delete non-available player")

        self.db.delete(player)
        self.db.commit()

        return {"status": "deleted"}