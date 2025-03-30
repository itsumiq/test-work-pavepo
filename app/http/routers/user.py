from typing import Annotated
from fastapi import APIRouter, Form, HTTPException, Response, UploadFile, status
from fastapi.responses import RedirectResponse

from app.exceptions import (
    BadMediaType,
    BadRequestException,
    ConflictException,
    InternalException,
    NotFoundException,
)
from app.http.deps import (
    AudioFileServiceDep,
    RefreshSessionServiceDep,
    TokenPayloadDep,
    UserServiceDep,
)
from app.models.audio_file import (
    AudioFileCreateRequestDTO,
    AudioFileCreateResponseDTO,
    AudioFilesGetResponseDTO,
)
from app.models.refresh_session import RefreshSessionRequestDTO
from app.models.user import (
    UserDeleteResponseDTO,
    UserGetResponseDTO,
    UserUpdateRequestDTO,
)
from app.settings.config import config

user_router = APIRouter(prefix="/users", tags=["Users"])


@user_router.patch("")
async def update_user_by_id(
    user: UserUpdateRequestDTO,
    user_service: UserServiceDep,
    token_payload: TokenPayloadDep,
):
    if not token_payload["is_superuser"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={"msg": "Not enough permissions to perform this action"},
        )

    try:
        user_response = await user_service.update_one_by_id(user=user)
    except InternalException:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"msg": "Internal server error"},
        )
    except NotFoundException:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail={"msg": "User not found"}
        )

    return user_response


@user_router.get("/{user_id}")
async def get_user_by_id(
    user_id: int, user_service: UserServiceDep, token_payload: TokenPayloadDep
) -> UserGetResponseDTO:
    if not token_payload["is_superuser"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={"msg": "Not enough permissions to perform this action"},
        )

    try:
        user_response = await user_service.get_one_by_id(id=user_id)
    except InternalException:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"msg": "Internal server error"},
        )
    except NotFoundException:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail={"msg": "User not found"}
        )

    return user_response


@user_router.delete("/{user_id}")
async def delete_user_by_id(
    user_id: int, user_service: UserServiceDep, token_payload: TokenPayloadDep
) -> UserDeleteResponseDTO:
    if not token_payload["is_superuser"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={"msg": "Not enough permissions to perform this action"},
        )
    try:
        user_response = await user_service.delete_one_by_id(id=user_id)
    except InternalException:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"msg": "Internal server error"},
        )
    except NotFoundException:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail={"msg": "User not found"}
        )

    return user_response


@user_router.get("/yandex/login")
async def get_yandex_login() -> RedirectResponse:
    params = f"response_type=code&client_id={config.YANDEX_CLIENT_ID}&redirect_uri={config.yandex_redirect_uri}&force_confirm=false"
    return RedirectResponse(url=f"{config.YANDEX_OAUTH_AUTHORIZE_URL}?{params}")


@user_router.get("/yandex/callback")
async def get_yandex_callback(
    code: str,
    user_service: UserServiceDep,
    session_service: RefreshSessionServiceDep,
    response: Response,
):
    try:
        user = await user_service.authenticate_with_yandex(code=code)
        tokens = await session_service.create_tokens(
            user_info=RefreshSessionRequestDTO(
                user_id=user.id, is_superuser=user.is_superuser
            )
        )
    except InternalException:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"msg": "Internal server error"},
        )

    response.headers["Authorization"] = f"Bearer {tokens.access_token}"
    return {"refresh_token": tokens.refresh_token}


@user_router.post("/audio")
async def upload_audio_file(
    file: UploadFile,
    custom_filename: Annotated[str, Form()],
    token_payload: TokenPayloadDep,
    audio_file_service: AudioFileServiceDep,
) -> AudioFileCreateResponseDTO:
    try:
        localfile = await audio_file_service.save_local(
            file=file, filename_custom=custom_filename, user_id=token_payload["id"]
        )
        file_response = await audio_file_service.save_db(
            file_info=AudioFileCreateRequestDTO(
                filepath=localfile.filepath,
                filename_unique=localfile.filename_unique,
                user_id=token_payload["id"],
                filename_original=custom_filename,
            )
        )
    except InternalException:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"msg": "Internal server error"},
        )
    except ConflictException:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={"msg": "Filename already exists"},
        )
    except BadRequestException:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"msg": "Filename missing"},
        )
    except BadMediaType:
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail={"msg": "Unsupported media type"},
        )

    return file_response


@user_router.get("/audio/{user_id}")
async def get_user_audio_files(
    user_id: int,
    token_payload: TokenPayloadDep,
    audio_file_service: AudioFileServiceDep,
) -> AudioFilesGetResponseDTO:
    if not token_payload["is_superuser"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={"msg": "Not enough permissions to perform this action"},
        )

    try:
        audio_files_response = await audio_file_service.get_all_by_user_id(
            user_id=user_id
        )
    except InternalException:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"msg": "Internal server error"},
        )

    return audio_files_response
