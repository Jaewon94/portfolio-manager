from sqlalchemy import String, Text, Integer, BigInteger, Boolean, Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column
from .base import Base, TimestampMixin
from typing import Optional
import enum


class MediaTargetType(enum.Enum):
    """미디어 대상 타입"""
    PROJECT = "project"
    NOTE = "note"


class MediaType(enum.Enum):
    """미디어 파일 타입"""
    IMAGE = "image"
    VIDEO = "video"
    DOCUMENT = "document"
    ARCHIVE = "archive"


class Media(Base, TimestampMixin):
    """
    미디어 파일 모델
    CLAUDE.md 명세: (id, target_type, target_id, original_name, file_path, file_size, mime_type, type, width, height, is_public, alt_text)
    """

    __tablename__ = "media"

    id: Mapped[int] = mapped_column(primary_key=True)
    
    # 대상 정보 (Polymorphic 관계)
    target_type: Mapped[MediaTargetType] = mapped_column(
        SQLEnum(MediaTargetType), nullable=False
    )
    target_id: Mapped[int] = mapped_column(Integer, nullable=False)  # project.id 또는 note.id
    
    # 파일 정보
    original_name: Mapped[str] = mapped_column(String(255), nullable=False)
    file_name: Mapped[str] = mapped_column(String(255), nullable=False)  # 저장된 파일명
    file_path: Mapped[str] = mapped_column(Text, nullable=False)  # 저장 경로
    file_size: Mapped[int] = mapped_column(BigInteger, nullable=False)  # bytes
    mime_type: Mapped[str] = mapped_column(String(100), nullable=False)
    type: Mapped[MediaType] = mapped_column(SQLEnum(MediaType), nullable=False)
    
    # 이미지/비디오 메타데이터
    width: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    height: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    duration: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)  # 비디오 길이 (초)
    
    # 설정
    is_public: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    alt_text: Mapped[Optional[str]] = mapped_column(Text, nullable=True)  # 접근성을 위한 대체 텍스트

    def __repr__(self):
        return f"<Media(id={self.id}, name={self.original_name}, type={self.type.value})>"

    @property
    def file_extension(self) -> str:
        """파일 확장자 추출"""
        if "." in self.original_name:
            return self.original_name.rsplit(".", 1)[1].lower()
        return ""

    @property
    def is_image(self) -> bool:
        """이미지 파일 여부"""
        return self.type == MediaType.IMAGE

    @property
    def is_video(self) -> bool:
        """비디오 파일 여부"""
        return self.type == MediaType.VIDEO

    @property
    def file_size_mb(self) -> float:
        """파일 크기를 MB 단위로 반환"""
        return round(self.file_size / (1024 * 1024), 2)