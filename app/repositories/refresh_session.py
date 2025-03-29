from abc import ABC, abstractmethod
from logging import getLogger

from sqlalchemy import insert, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.exceptions import InternalException
from app.models.refresh_session import RefreshSessionCreateDTO, RefreshSessionModel

logger = getLogger(__name__)


class BaseRefreshSessionRepository(ABC):
    @abstractmethod
    def __init__(self, *, session: AsyncSession):
        pass

    @abstractmethod
    async def create_one(self, *, session_info: RefreshSessionCreateDTO) -> None:
        pass

    @abstractmethod
    async def get_one(self, *, refresh_token: str) -> RefreshSessionModel | None:
        pass

    @abstractmethod
    async def update_one_by_id(self, *, id: int, refresh_token: str) -> None:
        pass


class RefreshSessionRepository(BaseRefreshSessionRepository):
    model = RefreshSessionModel

    def __init__(self, *, session: AsyncSession):
        self.session = session

    async def create_one(self, *, session_info: RefreshSessionCreateDTO) -> None:
        statement = insert(self.model).values(session_info.model_dump())
        try:
            await self.session.execute(statement)
        except Exception as e:
            logger.error("Database error: %s", e)
            raise InternalException

    async def get_one(self, *, refresh_token: str) -> RefreshSessionModel | None:
        statement = select(self.model).where(self.model.refresh_token == refresh_token)
        try:
            session = await self.session.scalar(statement)
        except Exception as e:
            logger.error("Database error: %s", e)
            raise InternalException

        return session

    async def update_one_by_id(self, *, id: int, refresh_token: str) -> None:
        statement = (
            update(self.model)
            .where(self.model.id == id)
            .values(refresh_token=refresh_token)
        )
        try:
            await self.session.execute(statement)
        except Exception as e:
            logger.error("Database error: %s", e)
            raise InternalException
