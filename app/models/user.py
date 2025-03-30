from datetime import datetime
from pydantic import BaseModel
from pydantic_extra_types.phone_numbers import PhoneNumber
from sqlalchemy import Boolean, String, Integer
from sqlalchemy.orm import Mapped, mapped_column

from app.database.base import Base


# database model
class UserModel(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    username: Mapped[str] = mapped_column(String, unique=True)
    phone_number: Mapped[PhoneNumber] = mapped_column(String, unique=True)
    yandex_id: Mapped[str] = mapped_column(String, unique=True)
    is_superuser: Mapped[bool] = mapped_column(Boolean, default=False)


# dto models
class UserCreateDTO(BaseModel):
    yandex_id: str
    username: str
    phone_number: PhoneNumber


class UserUpdateDTO(UserCreateDTO):
    pass


class UserUpdateRequestDTO(BaseModel):
    id: int
    username: str | None
    phone_number: PhoneNumber | None
    yandex_id: str | None
    is_superuser: bool | None


class UserUpdateResponseDTO(UserUpdateRequestDTO):
    pass


class UserDeleteResponseDTO(BaseModel):
    id: int


class UserAuthenticatedResponseDTO(UserCreateDTO):
    id: int
    is_superuser: bool


class UserGetResponseDTO(UserAuthenticatedResponseDTO):
    created_at: datetime
