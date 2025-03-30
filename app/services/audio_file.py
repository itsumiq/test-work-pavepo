from abc import ABC, abstractmethod
import os
from uuid import uuid4
from logging import getLogger

from fastapi import UploadFile

from app.exceptions import (
    BadMediaType,
    BadRequestException,
    ConflictException,
    InternalException,
)
from app.models.audio_file import (
    AudioFileCreateRequestDTO,
    AudioFileCreateResponseDTO,
    AudioFileSaveLocalDTO,
)
from app.repositories.uow import BaseUnitOfWork
from app.settings.config import config
import aiofiles

logger = getLogger(__name__)


class BaseAudioFileService(ABC):
    @abstractmethod
    def __init__(self, *, uow: BaseUnitOfWork):
        pass

    @abstractmethod
    async def save_local(
        self, *, file: UploadFile, filename_custom: str, user_id: int
    ) -> AudioFileSaveLocalDTO:
        pass

    @abstractmethod
    async def save_db(
        self, *, file_info: AudioFileCreateRequestDTO
    ) -> AudioFileCreateResponseDTO:
        pass


class AudioFileService(BaseAudioFileService):
    def __init__(self, *, uow: BaseUnitOfWork):
        self.uow = uow

    @staticmethod
    def _get_file_extension(*, filename: str) -> str:
        return os.path.splitext(filename)[1].lower()

    @staticmethod
    def _validate_file(*, file_extension: str, file_content_type: str | None):
        if (
            file_content_type
            and file_content_type not in config.ALLOWED_AUDIO_CONTENT_TYPES
        ) or file_extension not in config.ALLOWED_AUDIO_EXTENSIONS:
            raise BadMediaType

    async def save_local(
        self, *, file: UploadFile, filename_custom: str, user_id: int
    ) -> AudioFileSaveLocalDTO:
        async with self.uow:
            audio_repo = self.uow.get_audio_file_repo()
            audio_file = await audio_repo.get_one_by_user_id_and_filename(
                user_id=user_id, filename_original=filename_custom
            )
            if audio_file:
                raise ConflictException

        filename = file.filename
        if not filename:
            raise BadRequestException

        file_content_type = file.content_type
        file_extension = self._get_file_extension(filename=filename)
        self._validate_file(
            file_extension=file_extension, file_content_type=file_content_type
        )

        filename_unique = f"{uuid4()}{file_extension}"
        filepath = config.AUDIO_STORAGE_PATH_ABSOLUTE / filename_unique

        try:
            async with aiofiles.open(filepath, "wb") as localfile:
                while content := await file.read(1024 * 1024):
                    await localfile.write(content)
        except Exception as e:
            logger.error("File save failed: %s", e)
            if filepath.exists():
                os.remove(filepath)

            raise InternalException
        finally:
            await file.close()

        return AudioFileSaveLocalDTO(
            filepath=str(filepath), filename_unique=filename_unique
        )

    async def save_db(
        self, *, file_info: AudioFileCreateRequestDTO
    ) -> AudioFileCreateResponseDTO:
        async with self.uow:
            audio_repo = self.uow.get_audio_file_repo()
            audio_file = await audio_repo.create_one(audio_file_info=file_info)
            await self.uow.commit()

        return AudioFileCreateResponseDTO.model_validate(
            audio_file, from_attributes=True
        )
