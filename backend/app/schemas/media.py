"""
미디어 관련 Pydantic 스키마
파일 업로드, 이미지 처리, 메타데이터 관리
"""

from datetime import datetime
from typing import List, Optional

from app.models.media import MediaTargetType, MediaType
from pydantic import BaseModel, ConfigDict, Field, field_validator


class MediaUploadRequest(BaseModel):
    """미디어 업로드 요청"""

    target_type: MediaTargetType = Field(..., description="대상 타입 (project/note)")
    target_id: int = Field(..., ge=1, description="대상 ID")
    alt_text: Optional[str] = Field(
        None, max_length=500, description="접근성 대체 텍스트"
    )
    is_public: bool = Field(default=False, description="공개 여부")


class MediaResponse(BaseModel):
    """미디어 정보 응답"""

    id: int
    target_type: MediaTargetType
    target_id: int
    original_name: str
    file_path: str
    file_size: int
    mime_type: str
    type: MediaType
    width: Optional[int] = None
    height: Optional[int] = None
    duration: Optional[int] = None
    is_public: bool
    alt_text: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    # 계산된 필드
    file_extension: str
    is_image: bool
    is_video: bool
    file_size_mb: float
    download_url: str
    thumbnail_url: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class MediaListResponse(BaseModel):
    """미디어 목록 응답"""

    media: List[MediaResponse]
    total_count: int
    page: int
    page_size: int
    total_pages: int


class MediaUpdateRequest(BaseModel):
    """미디어 정보 수정 요청"""

    alt_text: Optional[str] = Field(
        None, max_length=500, description="접근성 대체 텍스트"
    )
    is_public: Optional[bool] = Field(None, description="공개 여부")


class MediaBulkDeleteRequest(BaseModel):
    """미디어 일괄 삭제 요청"""

    media_ids: List[int] = Field(
        ..., min_length=1, max_length=50, description="삭제할 미디어 ID 목록"
    )


class MediaStorageStats(BaseModel):
    """미디어 저장소 통계"""

    total_files: int
    total_size: int
    total_size_mb: float
    by_type: dict


class ImageProcessingOptions(BaseModel):
    """이미지 처리 옵션"""

    resize_width: Optional[int] = Field(
        None, ge=1, le=4096, description="리사이즈 너비"
    )
    resize_height: Optional[int] = Field(
        None, ge=1, le=4096, description="리사이즈 높이"
    )
    quality: Optional[int] = Field(
        None, ge=1, le=100, description="이미지 품질 (1-100)"
    )
    format: Optional[str] = Field(
        None, pattern="^(jpeg|png|webp)$", description="출력 포맷"
    )
    create_thumbnail: bool = Field(default=True, description="썸네일 생성 여부")

    @field_validator("resize_width", "resize_height")
    @classmethod
    def validate_dimensions(cls, v):
        if v is not None and v <= 0:
            raise ValueError("Dimensions must be positive")
        return v


class MediaErrorResponse(BaseModel):
    """미디어 에러 응답"""

    error: str
    detail: str
    file_name: Optional[str] = None
    max_file_size: Optional[int] = None
    allowed_types: Optional[List[str]] = None


class MediaUploadResult(BaseModel):
    """업로드 결과"""

    success: bool
    media: Optional[MediaResponse] = None
    error: Optional[MediaErrorResponse] = None
    processing_time_ms: int
