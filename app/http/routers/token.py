from fastapi import APIRouter, Response

from app.http.deps import RefreshSessionServiceDep
from app.models.refresh_session import RefreshSessionUpdateDTO

token_router = APIRouter(prefix="/tokens", tags=["Tokens"])


@token_router.patch("")
async def update_access_token(
    session_service: RefreshSessionServiceDep,
    token: RefreshSessionUpdateDTO,
    response: Response,
):
    tokens_new = await session_service.update_tokens(request=token)

    response.headers["Authorization"] = f"Bearer {tokens_new.access_token}"
    return {"refresh_token": tokens_new.refresh_token}
