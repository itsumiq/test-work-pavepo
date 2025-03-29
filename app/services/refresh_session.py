from abc import ABC, abstractmethod

from app.models.refresh_session import (
    RefreshSessionCreateDTO,
    RefreshSessionRequestDTO,
    RefreshSessionResponseDTO,
)
from app.repositories.uow import BaseUnitOfWork
from app.tokens.tokens import create_access_token, create_refresh_token


class BaseRefreshSessionService(ABC):
    @abstractmethod
    def __init__(self, *, uow: BaseUnitOfWork):
        pass

    @abstractmethod
    async def create_tokens(
        self, *, user_info: RefreshSessionRequestDTO
    ) -> RefreshSessionResponseDTO:
        pass


class RefreshSessionService(BaseRefreshSessionService):
    def __init__(self, *, uow: BaseUnitOfWork):
        self.uow = uow

    async def create_tokens(
        self, *, user_info: RefreshSessionRequestDTO
    ) -> RefreshSessionResponseDTO:
        refresh_token = create_refresh_token()

        async with self.uow:
            session_repo = self.uow.get_refresh_session_repo()
            await session_repo.create_one(
                session_info=RefreshSessionCreateDTO(
                    user_id=user_info.user_id,
                    refresh_token=refresh_token,
                )
            )
            await self.uow.commit()

        access_token = create_access_token(
            user_id=user_info.user_id,
            is_superuser=user_info.is_superuser,
        )

        return RefreshSessionResponseDTO(
            access_token=access_token,
            refresh_token=refresh_token,
        )
