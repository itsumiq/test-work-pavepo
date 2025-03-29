from abc import ABC, abstractmethod
from typing import Self

from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.refresh_session import (
    BaseRefreshSessionRepository,
    RefreshSessionRepository,
)
from app.repositories.user import BaseUserRepository, UserRepository
from app.database.db import session_factory


class BaseUnitOfWork(ABC):
    @abstractmethod
    async def __aenter__(self) -> Self:
        pass

    async def __aexit__(self, *args) -> None:
        pass

    @abstractmethod
    def get_user_repo(self) -> BaseUserRepository:
        pass

    @abstractmethod
    def get_refresh_session_repo(self) -> BaseRefreshSessionRepository:
        pass

    @abstractmethod
    async def commit(self) -> None:
        pass


class UnitOfWork(BaseUnitOfWork):
    async def __aenter__(self) -> Self:
        self.session: AsyncSession = session_factory()

        self.user_repo = UserRepository(session=self.session)
        self.refresh_session = RefreshSessionRepository(session=self.session)

        return self

    async def __aexit__(self, *args) -> None:
        await self.session.rollback()
        await self.session.close()

    def get_user_repo(self) -> BaseUserRepository:
        return self.user_repo

    def get_refresh_session_repo(self) -> BaseRefreshSessionRepository:
        return self.refresh_session

    async def commit(self) -> None:
        await self.session.commit()
