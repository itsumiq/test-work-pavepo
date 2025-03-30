from abc import ABC, abstractmethod
from logging import getLogger

import httpx

from app.exceptions import InternalException, NotFoundException
from app.models.user import (
    UserAuthenticatedResponseDTO,
    UserCreateDTO,
    UserDeleteResponseDTO,
    UserGetResponseDTO,
    UserUpdateDTO,
    UserUpdateRequestDTO,
    UserUpdateResponseDTO,
)
from app.repositories.uow import BaseUnitOfWork
from app.settings.config import config

logger = getLogger(__name__)


class BaseUserService(ABC):
    @abstractmethod
    def __init__(self, uow: BaseUnitOfWork):
        pass

    @abstractmethod
    async def authenticate_with_yandex(
        self, *, code: str
    ) -> UserAuthenticatedResponseDTO:
        pass

    @abstractmethod
    async def get_one_by_id(self, *, id: int) -> UserGetResponseDTO:
        pass

    @abstractmethod
    async def update_one_by_id(
        self, *, user: UserUpdateRequestDTO
    ) -> UserUpdateResponseDTO:
        pass

    @abstractmethod
    async def delete_one_by_id(self, *, id: int) -> UserDeleteResponseDTO:
        pass


class UserService:
    def __init__(self, uow: BaseUnitOfWork):
        self.uow = uow

    async def authenticate_with_yandex(
        self, *, code: str
    ) -> UserAuthenticatedResponseDTO:
        data_token_request = {
            "grant_type": "authorization_code",
            "code": code,
            "client_id": config.YANDEX_CLIENT_ID,
            "client_secret": config.YANDEX_CLIENT_SECRET,
        }

        try:
            # get tokens
            async with httpx.AsyncClient() as client:
                tokens_response = await client.post(
                    url=config.YANDEX_OAUTH_TOKEN_URL, data=data_token_request
                )
                tokens_response.raise_for_status()
                tokens = tokens_response.json()
                access_token_yandex = tokens["access_token"]

                if not access_token_yandex:
                    InternalException()

                # get user info
                headers = {"Authorization": f"OAuth {access_token_yandex}"}
                user_info_response = await client.get(
                    config.YANDEX_API_USERINFO_URL, headers=headers
                )
                user_info_response.raise_for_status()

                user_info = user_info_response.json()
                username = user_info["login"]
                phone_number = user_info["default_phone"]["number"]
                yandex_id = user_info["id"]

        except httpx.HTTPError as e:
            logger.error("Internal error: %s", e)
            raise InternalException()

        # check user in storage
        async with self.uow:
            user_repo = self.uow.get_user_repo()
            user_result = await user_repo.get_one_by_yandex_id(yandex_id=yandex_id)

            if user_result:
                if (
                    username != user_result.username
                    or phone_number != user_result.phone_number
                ):
                    user_updated = await user_repo.update_one_by_yandex_id(
                        user=UserUpdateDTO(
                            username=username,
                            phone_number=phone_number,
                            yandex_id=yandex_id,
                        )
                    )
                    return UserAuthenticatedResponseDTO.model_validate(
                        user_updated, from_attributes=True
                    )
                else:
                    await self.uow.commit()
                    return UserAuthenticatedResponseDTO.model_validate(
                        user_result, from_attributes=True
                    )

            user_created = await user_repo.create_one(
                user=UserCreateDTO(
                    username=username,
                    phone_number=phone_number,
                    yandex_id=yandex_id,
                )
            )

            await self.uow.commit()
            return UserAuthenticatedResponseDTO.model_validate(
                user_created, from_attributes=True
            )

    async def get_one_by_id(self, *, id: int) -> UserGetResponseDTO:
        async with self.uow:
            user_repo = self.uow.get_user_repo()
            user = await user_repo.get_one_by_id(id=id)

        if not user:
            raise NotFoundException

        return UserGetResponseDTO.model_validate(user, from_attributes=True)

    async def update_one_by_id(
        self, *, user: UserUpdateRequestDTO
    ) -> UserUpdateResponseDTO:
        async with self.uow:
            user_repo = self.uow.get_user_repo()
            user_updated = await user_repo.update_one_by_id(user=user)
            await self.uow.commit()

        if not user_updated:
            raise NotFoundException

        return UserUpdateResponseDTO.model_validate(user_updated, from_attributes=True)

    async def delete_one_by_id(self, *, id: int) -> UserDeleteResponseDTO:
        async with self.uow:
            user_repo = self.uow.get_user_repo()
            id_deleted = await user_repo.delete_one_by_id(id=id)
            await self.uow.commit()

        if not id_deleted:
            raise NotFoundException

        return UserDeleteResponseDTO(id=id_deleted)
