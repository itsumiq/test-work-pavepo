from abc import ABC, abstractmethod
from logging import getLogger

from sqlalchemy import delete, insert, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.exceptions import InternalException
from app.models.user import (
    UserCreateDTO,
    UserModel,
    UserUpdateDTO,
    UserUpdateRequestDTO,
)

logger = getLogger(__name__)


class BaseUserRepository(ABC):
    @abstractmethod
    def __init__(self, *, session: AsyncSession):
        pass

    @abstractmethod
    async def create_one(self, *, user: UserCreateDTO) -> UserModel:
        pass

    @abstractmethod
    async def get_one_by_yandex_id(self, *, yandex_id: str) -> UserModel | None:
        pass

    @abstractmethod
    async def get_one_by_id(self, *, id: int) -> UserModel | None:
        pass

    @abstractmethod
    async def update_one_by_yandex_id(self, *, user: UserUpdateDTO) -> UserModel:
        pass

    @abstractmethod
    async def update_one_by_id(self, *, user: UserUpdateRequestDTO) -> UserModel | None:
        pass

    @abstractmethod
    async def delete_one_by_id(self, *, id: int) -> int | None:
        pass


class UserRepository(BaseUserRepository):
    model = UserModel

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_one(self, *, user: UserCreateDTO) -> UserModel:
        statement = insert(self.model).values(user.model_dump()).returning(self.model)
        try:
            result = await self.session.execute(statement)
            user_created = result.scalar_one()
        except Exception as e:
            logger.error("Database Error %s", e)
            raise InternalException

        return user_created

    async def get_one_by_yandex_id(self, *, yandex_id: str) -> UserModel | None:
        statement = select(self.model).where(self.model.yandex_id == yandex_id)
        try:
            user = await self.session.scalar(statement)
        except Exception as e:
            logger.error("Database Error: %s", e)
            raise InternalException

        return user

    async def get_one_by_id(self, *, id: int) -> UserModel | None:
        statement = select(self.model).where(self.model.id == id)
        try:
            user = await self.session.scalar(statement)
        except Exception as e:
            logger.error("Database select error: %s", e)
            raise InternalException

        return user

    async def update_one_by_yandex_id(self, *, user: UserUpdateDTO) -> UserModel:
        statement = (
            update(self.model)
            .where(self.model.yandex_id == user.yandex_id)
            .values(user.model_dump(exclude={"yandex_id"}))
            .returning(self.model)
        )
        try:
            result = await self.session.execute(statement)
            user_updated = result.scalar_one()
        except Exception as e:
            logger.error("Database Error: %s", e)
            raise InternalException

        return user_updated

    async def update_one_by_id(self, *, user: UserUpdateRequestDTO) -> UserModel | None:
        statement = (
            update(self.model)
            .where(self.model.id == user.id)
            .values(user.model_dump(exclude_none=True, exclude={"id"}))
            .returning(self.model)
        )
        try:
            user_updated = await self.session.scalar(statement)
        except Exception as e:
            logger.error("Database update error: %s", e)
            raise InternalException

        return user_updated

    async def delete_one_by_id(self, *, id: int) -> int | None:
        statement = (
            delete(self.model).where(self.model.id == id).returning(self.model.id)
        )
        try:
            id_deleted = await self.session.scalar(statement)
        except Exception as e:
            logger.error("Database error: %s", e)
            raise InternalException

        return id_deleted
