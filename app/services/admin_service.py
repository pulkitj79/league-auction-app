import os
import pandas as pd
from sqlalchemy.orm import Session
from passlib.context import CryptContext

from app.models.team import Team
from app.models.player import Player
from app.models.pool import Pool
from app.core.constants import PlayerStatus


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class AdminService:

    def __init__(self, db: Session):
        self.db = db

    # ----------------------------------------
    # LOAD FROM ROOT DATA FOLDER
    # ----------------------------------------
    def load_from_root(self):

        base_path = os.path.join(os.getcwd(), "data")

        teams_path = os.path.join(base_path, "teams.csv")
        players_path = os.path.join(base_path, "players.csv")

        if not os.path.exists(teams_path):
            raise Exception("teams.csv not found in /data")

        if not os.path.exists(players_path):
            raise Exception("players.csv not found in /data")

        self._clear_existing_data()
        self._load_teams(teams_path)
        self._load_players(players_path)

        return {"status": "Data loaded successfully from root"}

    # ----------------------------------------
    # CLEAR EXISTING DATA
    # ----------------------------------------
    def _clear_existing_data(self):
        self.db.query(Player).delete()
        self.db.query(Team).delete()
        self.db.query(Pool).delete()
        self.db.commit()

    # ----------------------------------------
    # LOAD TEAMS
    # ----------------------------------------
    def _load_teams(self, filepath):

        df = pd.read_csv(filepath, dtype=str)

        required = {"name", "budget_remaining", "color", "pin"}
        if not required.issubset(df.columns):
            raise Exception("Invalid teams.csv schema")

        for _, row in df.iterrows():

            pin_raw = str(row["pin"]).strip()
            print("DEBUG PIN VALUE:", pin_raw, "LEN:", len(pin_raw))

            if not pin_raw:
                raise Exception(f"Empty PIN for team {row['name']}")

            if len(pin_raw) > 50:
                raise Exception(f"PIN too long for team {row['name']}")

            # Optional: enforce numeric PIN
            if not pin_raw.isdigit():
                raise Exception(f"PIN must be numeric for team {row['name']}")

            team = Team(
                name=row["name"].strip(),
                budget_remaining=float(row["budget_remaining"]),
                color=row["color"].strip(),
                pin_hash=pwd_context.hash(pin_raw)
            )

            self.db.add(team)

        self.db.commit()

    # ----------------------------------------
    # LOAD PLAYERS
    # ----------------------------------------
    def _load_players(self, filepath):

        df = pd.read_csv(filepath)

        required = {"name", "role", "base_price", "pool"}
        if not required.issubset(df.columns):
            raise Exception("Invalid players.csv schema")

        unique_pools = df["pool"].unique()
        pool_map = {}

        for index, pool_name in enumerate(unique_pools):
            pool = Pool(
                name=pool_name,
                sequence_order=index + 1,
                is_active=True
            )
            self.db.add(pool)
            self.db.commit()
            self.db.refresh(pool)
            pool_map[pool_name] = pool.id

        for _, row in df.iterrows():
            player = Player(
                name=row["name"],
                role=row["role"],
                base_price=float(row["base_price"]),
                pool_id=pool_map[row["pool"]],
                status=PlayerStatus.AVAILABLE.value
            )
            self.db.add(player)

        self.db.commit()
