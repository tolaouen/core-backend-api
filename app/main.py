
import logging
from pathlib import Path

from alembic import command
from alembic.config import Config
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.api.v1.api import api_route

logger = logging.getLogger(__name__)


def run_database_migrations() -> None:
    """Run Alembic migrations before the app accepts traffic."""
    try:
        alembic_cfg = Config(str(Path(__file__).resolve().parent.parent / "alembic.ini"))
        alembic_cfg.set_main_option(
            "sqlalchemy.url", settings.DATABASE_URL.replace("%", "%%")
        )
        command.upgrade(alembic_cfg, "head")
        logger.info("Database migrations completed successfully.")
    except Exception:
        logger.exception("Database migrations failed on startup.")
        raise


app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    docs_url="/docs",
    redoc_url="/redoc"
)


# Development (More permissive)
if settings.ENVIRONMENT == "development":
    allow_methods = ["*"]
else:  # Production (Restricted)
    allow_methods = ["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"]

origins = [str(o).rstrip("/") for o in settings.BACKEND_CORS_ORIGINS]

# CORS MIDDLEWARE
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=allow_methods,
    allow_headers=["*"],
)

# Routers
app.include_router(api_route, prefix=settings.API_V1_STR)


# @app.on_event("startup")
# async def startup_event() -> None:
#     run_database_migrations()


@app.get("/", tags=["Root"])
def root():
    return {
        "message": settings.PROJECT_NAME,
        # "version": settings.VERSION,
        # "api": settings.API_V1_STR
        "status": 404,
        "detail": "Not Found"
    }