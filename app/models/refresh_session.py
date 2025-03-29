from datetime import datetime

from pydantic import BaseModel
from sqlalchemy import DateTime, ForeignKey, String, Integer, text
from sqlalchemy.orm import Mapped, mapped_column


from app.database.base import Base


class RefreshSessionModel(Base):
    __tablename__ = "refresh_sessions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), index=True)
    refresh_token: Mapped[str] = mapped_column(String, index=True)
    expire_in: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=text("(now() AT TIME ZONE 'utc') + interval '15 minutes'"),
        onupdate=text("(now() AT TIME ZONE 'utc') + interval '15 minutes'"),
    )


class RefreshSessionRequestDTO(BaseModel):
    user_id: int
    is_superuser: bool


class RefreshSessionCreateDTO(BaseModel):
    user_id: int
    refresh_token: str


class RefreshSessionResponseDTO(BaseModel):
    access_token: str
    refresh_token: str


class RefreshSessionUpdateDTO(BaseModel):
    refresh_token: str
