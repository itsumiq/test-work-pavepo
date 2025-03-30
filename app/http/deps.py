from typing import Annotated
from logging import getLogger

from fastapi import Depends, HTTPException, Header, status

from app.exceptions import AuthException
from app.repositories.uow import UnitOfWork
from app.services.audio_file import AudioFileService, BaseAudioFileService
from app.services.refresh_session import (
    BaseRefreshSessionService,
    RefreshSessionService,
)
from app.services.user import BaseUserService, UserService
from app.tokens.tokens import TokenPayload, validate_access_token

logger = getLogger(__name__)


# user service
def get_user_service():
    return UserService(UnitOfWork())


UserServiceDep = Annotated[BaseUserService, Depends(get_user_service)]


# refresh session service
def get_refresh_session_service():
    return RefreshSessionService(uow=UnitOfWork())


RefreshSessionServiceDep = Annotated[
    BaseRefreshSessionService, Depends(get_refresh_session_service)
]


# audio file service
def get_audio_file_service():
    return AudioFileService(uow=UnitOfWork())


AudioFileServiceDep = Annotated[BaseAudioFileService, Depends(get_audio_file_service)]


# access token validation
def get_token_payload(authorization: Annotated[str, Header()]) -> TokenPayload:
    parts = authorization.split(" ")
    if len(parts) != 2 or parts[0] != "Bearer":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"msg": "Token validation error"},
        )

    access_token = parts[1]
    try:
        payload = validate_access_token(token=access_token)
    except AuthException:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"msg": "Token validation error"},
        )
    except Exception as e:
        logger.error("Unknown error: %s", e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"msg": "Internal server error"},
        )

    return payload


TokenPayloadDep = Annotated[TokenPayload, Depends(get_token_payload)]
