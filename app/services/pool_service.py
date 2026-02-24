from sqlalchemy.orm import Session
from app.models.pool import Pool
from app.models.player import Player


class PoolService:

    def __init__(self, db: Session):
        self.db = db

    def get_all(self):
        return self.db.query(Pool).order_by(Pool.sequence_order).all()

    def create(self, name: str, sequence_order: int, is_active: bool = True):
        pool = Pool(
            name=name,
            sequence_order=sequence_order,
            is_active=is_active
        )

        self.db.add(pool)
        self.db.commit()
        self.db.refresh(pool)
        return pool

    def delete(self, pool_id: int):
        pool = self.db.query(Pool).filter(Pool.id == pool_id).first()

        if not pool:
            raise Exception("Pool not found")

        # Safety check — cannot delete pool with players
        player_exists = (
            self.db.query(Player)
            .filter(Player.pool_id == pool_id)
            .first()
        )

        if player_exists:
            raise Exception("Cannot delete pool with assigned players")

        self.db.delete(pool)
        self.db.commit()

        return {"status": "deleted"}

    def toggle_active(self, pool_id: int):
        pool = self.db.query(Pool).filter(Pool.id == pool_id).first()

        if not pool:
            raise Exception("Pool not found")

        pool.is_active = not pool.is_active
        self.db.commit()
        self.db.refresh(pool)

        return pool