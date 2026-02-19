from fastapi import APIRouter, UploadFile, File, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.utils.importer import DataImporter
from app.core.settings import settings

router = APIRouter(prefix="/api/import", tags=["Data Import"])


@router.post("/players")
async def import_players(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    if not settings.features.get("enable_csv_upload"):
        raise HTTPException(status_code=403, detail="CSV upload disabled")

    try:
        return DataImporter.import_players(file, db)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/teams")
async def import_teams(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    if not settings.features.get("enable_csv_upload"):
        raise HTTPException(status_code=403, detail="CSV upload disabled")

    try:
        return DataImporter.import_teams(file, db)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
