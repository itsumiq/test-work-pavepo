from fastapi import APIRouter, HTTPException, Response, status
from fastapi.responses import RedirectResponse

from app.exceptions import InternalException
from app.http.deps import RefreshSessionServiceDep, UserServiceDep
from app.models.refresh_session import RefreshSessionRequestDTO
from app.settings.config import config

user_router = APIRouter(prefix="/users", tags=["Users"])


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
