from abc import ABC, abstractmethod
from logging import getLogger

import httpx

from app.exceptions import InternalException
from app.models.user import (
    UserAuthenticatedResponseDTO,
    UserCreateDTO,
    UserUpdateInfoDTO,
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
            async with httpx.AsyncClient() as client:
                # get tokens
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
            user_result = await user_repo.get_by_yandex_id(yandex_id=yandex_id)

            if user_result:
                if (
                    username != user_result.username
                    or phone_number != user_result.phone_number
                ):
                    user_updated = await user_repo.update_info(
                        user_info=UserUpdateInfoDTO(
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
                user_info=UserCreateDTO(
                    username=username,
                    phone_number=phone_number,
                    yandex_id=yandex_id,
                )
            )

            await self.uow.commit()
            return UserAuthenticatedResponseDTO.model_validate(
                user_created, from_attributes=True
            )
