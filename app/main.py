from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.endpoints.contracts import router as contracts_router
from app.api.v1.endpoints.customers import router as customers_router
from app.api.v1.endpoints.payments import router as payments_router
from app.api.v1.endpoints.line_webhook import router as line_webhook_router
from app.core.config import settings
from app.db.base import Base
from app.db.seed import seed_demo_data
from app.db.session import AsyncSessionLocal, engine

from app.models import ApiLog, ContractMaster  # noqa: F401


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    if settings.seed_on_startup:
        async with AsyncSessionLocal() as session:
            await seed_demo_data(session)

    yield

    await engine.dispose()


app = FastAPI(
    title=settings.app_name,
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:8081",
        "http://127.0.0.1:8081",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(customers_router, prefix="/api/v1")
app.include_router(contracts_router, prefix="/api/v1")
app.include_router(payments_router, prefix="/api/v1")
app.include_router(line_webhook_router, prefix="/api/v1")

@app.get("/health", tags=["System"])
async def health() -> dict:
    return {
        "status": "ok",
        "app": settings.app_name,
        "env": settings.app_env,
    }


@app.get("/", tags=["System"])
async def root() -> dict:
    return {
        "message": f"{settings.app_name} is running",
        "docs": "/docs",
        "health": "/health",
    }