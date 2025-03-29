from logging import getLogger

from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from app.database.base import Base
from app.settings.config import config

logger = getLogger(__name__)

engine = create_async_engine(url=config.DB_URL)
session_factory = async_sessionmaker(
    bind=engine, autoflush=False, expire_on_commit=False
)


async def create_tables():
    async with engine.begin() as conn:
        try:
            await conn.run_sync(Base.metadata.create_all)
        except Exception as e:
            logger.error("Create tables failed: %s", e)
            raise e


async def drop_tables():
    async with engine.begin() as conn:
        try:
            await conn.run_sync(Base.metadata.drop_all)
        except Exception as e:
            logger.error("Drop tables failed: %s", e)
            raise e


async def close_pool():
    await engine.dispose()
