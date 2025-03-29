from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.database.db import close_pool, create_tables, drop_tables
from app.http.routers.routers import routers


@asynccontextmanager
async def lifrespawn(app: FastAPI):
    await create_tables()

    yield

    await drop_tables()
    await close_pool()


app = FastAPI(root_path="/api", lifespan=lifrespawn)

for router in routers:
    app.include_router(router)
