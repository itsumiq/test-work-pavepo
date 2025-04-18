from pydantic import BaseModel
from sqlalchemy import Integer, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from app.database.base import Base


# database model
class AudioFileModel(Base):
    __tablename__ = "audio_files"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), index=True)
    filename_original: Mapped[str] = mapped_column(String)
    filename_unique: Mapped[str] = mapped_column(String, unique=True)
    filepath: Mapped[str] = mapped_column(String)


# dto models
class AudioFileSaveLocalDTO(BaseModel):
    filepath: str
    filename_unique: str


class AudioFileCreateRequestDTO(AudioFileSaveLocalDTO):
    user_id: int
    filename_original: str


class AudioFileCreateResponseDTO(BaseModel):
    filename_original: str
    filename_unique: str


class AudioFileGetDTO(BaseModel):
    filepath: str
    filename_original: str


class AudioFilesGetResponseDTO(BaseModel):
    user_id: int
    files: list[AudioFileGetDTO]
