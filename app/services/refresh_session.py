from abc import ABC, abstractmethod
from datetime import datetime, timezone

from app.exceptions import AuthException
from app.models.refresh_session import (
    RefreshSessionCreateDTO,
    RefreshSessionRequestDTO,
    RefreshSessionResponseDTO,
    RefreshSessionUpdateDTO,
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

    @abstractmethod
    async def update_tokens(
        self, *, request: RefreshSessionUpdateDTO
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

    async def update_tokens(
        self, *, request: RefreshSessionUpdateDTO
    ) -> RefreshSessionResponseDTO:
        async with self.uow:
            session_repo = self.uow.get_refresh_session_repo()
            session = await session_repo.get_one(refresh_token=request.refresh_token)
            if not session or session.expire_in < datetime.now(tz=timezone.utc):
                raise AuthException

            user_repo = self.uow.get_user_repo()
            user = await user_repo.get_by_id(id=session.user_id)
            if not user:
                raise AuthException

            refresh_token_new = create_refresh_token()
            await session_repo.update_one_by_id(
                id=session.id, refresh_token=refresh_token_new
            )

            access_token = create_access_token(
                user_id=user.id, is_superuser=user.is_superuser
            )
            await self.uow.commit()

        return RefreshSessionResponseDTO(
            access_token=access_token, refresh_token=refresh_token_new
        )
