from datetime import datetime, timedelta, timezone
from logging import getLogger
from typing import TypedDict
from uuid import uuid4

from jwt import decode, encode
from jwt.exceptions import InvalidTokenError

from app.exceptions import AuthException
from app.settings.config import config

ALGORITHM = "HS256"

logger = getLogger(__name__)


class TokenPayload(TypedDict):
    id: int
    is_superuser: bool
    iat: datetime
    exp: datetime


def create_refresh_token() -> str:
    return str(uuid4())


def create_access_token(*, user_id: int, is_superuser: bool) -> str:
    time_now = datetime.now(tz=timezone.utc)
    token_payload = {
        "id": user_id,
        "is_superuser": is_superuser,
        "iat": time_now,
        "exp": time_now + timedelta(minutes=15),
    }

    return encode(
        payload=token_payload,
        key=config.JWT_SECRET_KEY,
        algorithm=ALGORITHM,
    )


def validate_access_token(*, token: str) -> TokenPayload:
    try:
        token_payload: TokenPayload = decode(
            token, key=config.JWT_SECRET_KEY, algorithms=ALGORITHM
        )
    except InvalidTokenError:
        raise AuthException

    return token_payload
