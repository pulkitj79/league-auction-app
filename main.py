from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from app.db.session import engine, Base, SessionLocal
from app.websocket.manager import manager

from app.routers import auction
from app.routers import import_data
from app.routers import auth
from app.routers import admin

from app.models.auction_config import AuctionConfig


app = FastAPI(title="League Auction App")


# ------------------------------------------------
# CREATE DB TABLES FIRST
# ------------------------------------------------
Base.metadata.create_all(bind=engine)


# ------------------------------------------------
# ENSURE DEFAULT CONFIG (AFTER TABLE CREATION)
# ------------------------------------------------
def ensure_default_config():
    db = SessionLocal()
    try:
        config = db.query(AuctionConfig).first()
        if not config:
            default_config = AuctionConfig()
            db.add(default_config)
            db.commit()
    finally:
        db.close()


ensure_default_config()


# ------------------------------------------------
# ROUTERS
# ------------------------------------------------
app.include_router(auction.router)
app.include_router(import_data.router)
app.include_router(auth.router)
app.include_router(admin.router)


# ------------------------------------------------
# TEMPLATES
# ------------------------------------------------
templates = Jinja2Templates(directory="templates")


# ------------------------------------------------
# STATIC FILES
# ------------------------------------------------
app.mount("/static", StaticFiles(directory="static"), name="static")


# ------------------------------------------------
# FRONTEND ROUTES
# ------------------------------------------------
@app.get("/auctioneer", response_class=HTMLResponse)
async def auctioneer_page(request: Request):
    return templates.TemplateResponse("auctioneer.html", {"request": request})


@app.get("/bidder", response_class=HTMLResponse)
async def bidder_page(request: Request):
    return templates.TemplateResponse("bidder.html", {"request": request})


@app.get("/projector", response_class=HTMLResponse)
async def projector_page(request: Request):
    return templates.TemplateResponse("projector.html", {"request": request})


# ------------------------------------------------
# WEBSOCKET
# ------------------------------------------------
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket)


# ------------------------------------------------
# HEALTH CHECK
# ------------------------------------------------
@app.get("/")
def root():
    return {"status": "Auction server running"}
