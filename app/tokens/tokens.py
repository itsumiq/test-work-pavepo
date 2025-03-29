from datetime import datetime, timedelta, timezone
from logging import getLogger
from dataclasses import dataclass
from uuid import uuid4

from jwt import encode

from app.settings.config import config

logger = getLogger(__name__)

# @dataclass
# TokenPayload:
#


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
        algorithm="HS256",
    )
