from abc import ABC, abstractmethod
from logging import getLogger

from sqlalchemy import and_, insert, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.exceptions import InternalException
from app.models.audio_file import AudioFileCreateRequestDTO, AudioFileModel


logger = getLogger(__name__)


class BaseAudioFileRepository(ABC):
    @abstractmethod
    def __init__(self, *, session: AsyncSession):
        pass

    @abstractmethod
    async def create_one(
        self, *, audio_file_info: AudioFileCreateRequestDTO
    ) -> AudioFileModel:
        pass

    @abstractmethod
    async def get_one_by_user_id_and_filename(
        self, *, user_id: int, filename_original: str
    ) -> AudioFileModel | None:
        pass

    @abstractmethod
    async def get_all_by_user_id(self, *, user_id: int) -> list[AudioFileModel]:
        pass


class AudioFileRepository(BaseAudioFileRepository):
    model = AudioFileModel

    def __init__(self, *, session: AsyncSession):
        self.session = session

    async def create_one(
        self, *, audio_file_info: AudioFileCreateRequestDTO
    ) -> AudioFileModel:
        statement = (
            insert(self.model)
            .values(audio_file_info.model_dump())
            .returning(self.model)
        )
        try:
            result = await self.session.execute(statement)
            audio_file = result.scalar_one()
        except Exception as e:
            logger.error("Database insert error: %s", e)
            raise InternalException

        return audio_file

    async def get_one_by_user_id_and_filename(
        self, *, user_id: int, filename_original: str
    ) -> AudioFileModel | None:
        statement = (
            select(self.model)
            .where(
                and_(
                    self.model.user_id == user_id,
                    self.model.filename_original == filename_original,
                )
            )
            .limit(1)
        )
        try:
            audio_file = await self.session.scalar(statement)
        except Exception as e:
            logger.error("Database select error: %s", e)
            raise InternalException

        return audio_file

    async def get_all_by_user_id(self, *, user_id: int) -> list[AudioFileModel]:
        statement = select(self.model).where(self.model.user_id == user_id)
        try:
            result = await self.session.scalars(statement)
            audio_files = list(result.all())
        except Exception as e:
            logger.error("Database select error: %s", e)
            raise InternalException

        return audio_files
