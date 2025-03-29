from pydantic import BaseModel
from pydantic_extra_types.phone_numbers import PhoneNumber
from sqlalchemy import Boolean, String, Integer
from sqlalchemy.orm import Mapped, mapped_column

from app.database.base import Base


# dto models
class UserCreateDTO(BaseModel):
    yandex_id: str
    username: str
    phone_number: PhoneNumber


class UserUpdateInfoDTO(UserCreateDTO):
    pass


class UserAuthenticatedResponseDTO(UserCreateDTO):
    id: int
    is_superuser: bool


# database model
class UserModel(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    username: Mapped[str] = mapped_column(String, unique=True)
    phone_number: Mapped[PhoneNumber] = mapped_column(String, unique=True)
    yandex_id: Mapped[str] = mapped_column(String, unique=True)
    is_superuser: Mapped[bool] = mapped_column(Boolean, default=False)
