from abc import ABC, abstractmethod
from logging import getLogger

from sqlalchemy import insert, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.exceptions import InternalException
from app.models.user import UserCreateDTO, UserModel, UserUpdateInfoDTO

logger = getLogger(__name__)


class BaseUserRepository(ABC):
    @abstractmethod
    def __init__(self, *, session: AsyncSession):
        pass

    @abstractmethod
    async def create_one(self, *, user_info: UserCreateDTO) -> UserModel:
        pass

    @abstractmethod
    async def get_by_yandex_id(self, *, yandex_id: str) -> UserModel | None:
        pass

    @abstractmethod
    async def update_info(self, *, user_info: UserUpdateInfoDTO) -> UserModel:
        pass

    @abstractmethod
    async def get_by_id(self, *, id: int) -> UserModel | None:
        pass


class UserRepository(BaseUserRepository):
    model = UserModel

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_one(self, *, user_info: UserCreateDTO) -> UserModel:
        statement = (
            insert(self.model).values(user_info.model_dump()).returning(self.model)
        )
        try:
            result = await self.session.execute(statement)
            user = result.scalar_one()
        except Exception as e:
            logger.error("Database Error %s", e)
            raise InternalException

        return user

    async def get_by_yandex_id(self, *, yandex_id: str) -> UserModel | None:
        statement = select(self.model).where(self.model.yandex_id == yandex_id)
        try:
            user = await self.session.scalar(statement)
        except Exception as e:
            logger.error("Database Error: %s", e)
            raise InternalException

        return user

    async def get_by_id(self, *, id: int) -> UserModel | None:
        statement = select(self.model).where(self.model.id == id)
        try:
            user = await self.session.scalar(statement)
        except Exception as e:
            raise InternalException

        return user

    async def update_info(self, *, user_info: UserUpdateInfoDTO) -> UserModel:
        statement = (
            update(self.model)
            .where(self.model.yandex_id == user_info.yandex_id)
            .values(user_info.model_dump(exclude={"yandex_id"}))
            .returning(self.model)
        )
        try:
            result = await self.session.execute(statement)
            user = result.scalar_one()
        except Exception as e:
            logger.error("Database Error: %s", e)
            raise InternalException

        return user
