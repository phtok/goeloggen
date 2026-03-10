from fastapi import FastAPI
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles

from app.api.router import api_router
from app.core.settings import get_settings
from app.db.base import Base
from app.db.session import engine
import app.models  # noqa: F401

settings = get_settings()

app = FastAPI(title=settings.app_name, version="0.1.0")
app.include_router(api_router, prefix="/v1")
app.mount(
    settings.storage_public_base_url,
    StaticFiles(directory=settings.storage_root),
    name="artifacts",
)


@app.on_event("startup")
def startup() -> None:
    Base.metadata.create_all(bind=engine)
    settings.storage_root.mkdir(parents=True, exist_ok=True)


@app.get("/healthz")
def healthz() -> JSONResponse:
    return JSONResponse({"ok": True, "env": settings.app_env})
