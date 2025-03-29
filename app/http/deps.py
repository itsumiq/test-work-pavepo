from typing import Annotated

from fastapi import Depends
from app.repositories.uow import UnitOfWork
from app.services.refresh_session import (
    BaseRefreshSessionService,
    RefreshSessionService,
)
from app.services.user import BaseUserService, UserService


def get_user_service():
    return UserService(UnitOfWork())


UserServiceDep = Annotated[BaseUserService, Depends(get_user_service)]


def get_refresh_session_service():
    return RefreshSessionService(uow=UnitOfWork())


RefreshSessionServiceDep = Annotated[
    BaseRefreshSessionService, Depends(get_refresh_session_service)
]
