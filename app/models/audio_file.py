from sqlalchemy import Integer, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from app.database.base import Base


class AudioFile(Base):
    __tablename__ = "audio_files"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), index=True)
    filename_original: Mapped[str] = mapped_column(String)
    filename_unique: Mapped[str] = mapped_column(String, unique=True)
    filepath: Mapped[str] = mapped_column(String)
