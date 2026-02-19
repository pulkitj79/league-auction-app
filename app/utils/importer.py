import pandas as pd
from sqlalchemy.orm import Session
from app.models.player import Player
from app.models.team import Team
from app.models.pool import Pool
from app.core.constants import PlayerStatus, Defaults


class DataImporter:

    REQUIRED_PLAYER_COLUMNS = {"name", "base_price", "pool"}
    REQUIRED_TEAM_COLUMNS = {"name", "budget_remaining"}

    @staticmethod
    def _validate_columns(df, required_columns):
        missing = required_columns - set(df.columns)
        if missing:
            raise Exception(f"Missing required columns: {missing}")

    @staticmethod
    def import_players(file, db: Session):
        df = DataImporter._read_file(file)

        DataImporter._validate_columns(df, DataImporter.REQUIRED_PLAYER_COLUMNS)

        db.query(Player).delete()
        db.query(Pool).delete()

        unique_pools = df["pool"].unique()
        pool_map = {}

        for idx, pool_name in enumerate(unique_pools):
            pool = Pool(name=pool_name, sequence_order=idx + 1)
            db.add(pool)
            db.commit()
            db.refresh(pool)
            pool_map[pool_name] = pool.id

        players = []
        for _, row in df.iterrows():
            players.append(
                Player(
                    name=row["name"],
                    role=row.get("role", ""),
                    base_price=float(row["base_price"]),
                    pool_id=pool_map[row["pool"]],
                    status=PlayerStatus.AVAILABLE.value
                )
            )

        db.bulk_save_objects(players)
        db.commit()

        return {
            "imported_players": len(players),
            "pools_created": len(unique_pools)
        }

    @staticmethod
    def import_teams(file, db: Session):
        df = DataImporter._read_file(file)

        DataImporter._validate_columns(df, DataImporter.REQUIRED_TEAM_COLUMNS)

        db.query(Team).delete()

        teams = []
        for _, row in df.iterrows():
            teams.append(
                Team(
                    name=row["name"],
                    budget_remaining=float(row["budget_remaining"]),
                    color=row.get("color", Defaults.TEAM_COLOR)
                )
            )

        db.bulk_save_objects(teams)
        db.commit()

        return {"imported_teams": len(teams)}

    @staticmethod
    def _read_file(file):
        filename = file.filename.lower()

        if filename.endswith(".csv"):
            return pd.read_csv(file.file)

        if filename.endswith(".xlsx"):
            return pd.read_excel(file.file)

        raise Exception("Unsupported file format. Use CSV or Excel.")
