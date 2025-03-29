from abc import ABC, abstractmethod
from logging import getLogger

from sqlalchemy import insert
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
