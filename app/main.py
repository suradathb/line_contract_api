from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.v1.endpoints import contracts, customers, line_mappings, payments
from app.core.config import settings
from app.db.base import Base
from app.db.seed import seed_demo_data
from app.db.session import AsyncSessionLocal, engine
from app.models import ApiLog, Contract, LineMapping, PaymentSchedule  # noqa: F401


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    if settings.seed_on_startup:
        async with AsyncSessionLocal() as session:
            await seed_demo_data(session)

    yield

    await engine.dispose()


app = FastAPI(title=settings.app_name, version="1.0.0", lifespan=lifespan)

app.include_router(customers.router, prefix="/api/v1")
app.include_router(line_mappings.router, prefix="/api/v1")
app.include_router(contracts.router, prefix="/api/v1")
app.include_router(payments.router, prefix="/api/v1")


@app.get("/health")
async def health() -> dict:
    return {"status": "ok", "app": settings.app_name, "env": settings.app_env}
