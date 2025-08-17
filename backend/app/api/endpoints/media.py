"""
미디어 API 엔드포인트
파일 업로드, 다운로드, 이미지 처리, 저장소 관리
"""

import os
from pathlib import Path
from typing import Optional, List
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form, Query
from fastapi.responses import FileResponse, StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.services.auth import get_current_user, get_current_user_optional
from app.services.media import MediaService
from app.models.user import User
from app.models.media import MediaTargetType, MediaType
from app.schemas.media import (
    MediaResponse, MediaListResponse, MediaUpdateRequest,
    MediaBulkDeleteRequest, MediaStorageStats, MediaUploadResult,
    ImageProcessingOptions
)

router = APIRouter()


@router.post("/upload", response_model=MediaUploadResult)
async def upload_media(
    file: UploadFile = File(..., description="업로드할 파일"),
    target_type: MediaTargetType = Form(..., description="대상 타입 (project/note)"),
    target_id: int = Form(..., description="대상 ID"),
    alt_text: Optional[str] = Form(None, description="접근성 대체 텍스트"),
    is_public: bool = Form(default=False, description="공개 여부"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    미디어 파일 업로드
    
    - 이미지, 비디오, 문서, 아카이브 파일 지원
    - 자동 이미지 처리 및 썸네일 생성
    - 파일 크기 및 타입 검증
    """
    start_time = datetime.now()
    
    try:
        media_service = MediaService(db)
        
        media = await media_service.upload_file(
            file=file,
            target_type=target_type,
            target_id=target_id,
            user_id=current_user.id,
            alt_text=alt_text,
            is_public=is_public
        )
        
        # 응답 데이터 구성
        media_response = MediaResponse(
            id=media.id,
            target_type=media.target_type,
            target_id=media.target_id,
            original_name=media.original_name,
            file_path=media.file_path,
            file_size=media.file_size,
            mime_type=media.mime_type,
            type=media.type,
            width=media.width,
            height=media.height,
            duration=media.duration,
            is_public=media.is_public,
            alt_text=media.alt_text,
            created_at=media.created_at,
            updated_at=media.updated_at,
            file_extension=media.file_extension,
            is_image=media.is_image,
            is_video=media.is_video,
            file_size_mb=media.file_size_mb,
            download_url=media_service.get_download_url(media),
            thumbnail_url=media_service.get_thumbnail_url(media)
        )
        
        processing_time = (datetime.now() - start_time).total_seconds() * 1000
        
        return MediaUploadResult(
            success=True,
            media=media_response,
            error=None,
            processing_time_ms=int(processing_time)
        )
        
    except HTTPException as e:
        processing_time = (datetime.now() - start_time).total_seconds() * 1000
        
        return MediaUploadResult(
            success=False,
            media=None,
            error={
                "error": "Upload failed",
                "detail": e.detail,
                "file_name": file.filename
            },
            processing_time_ms=int(processing_time)
        )


@router.get("/", response_model=MediaListResponse)
async def get_media_list(
    target_type: Optional[MediaTargetType] = Query(None, description="대상 타입 필터"),
    target_id: Optional[int] = Query(None, description="대상 ID 필터"),
    media_type: Optional[MediaType] = Query(None, description="미디어 타입 필터"),
    only_public: bool = Query(default=True, description="공개 파일만 조회"),
    page: int = Query(default=1, ge=1, description="페이지 번호"),
    page_size: int = Query(default=20, ge=1, le=100, description="페이지 크기"),
    current_user: Optional[User] = Depends(get_current_user_optional),
    db: AsyncSession = Depends(get_db)
):
    """
    미디어 목록 조회
    
    - 타입별, 대상별 필터링 지원
    - 공개/비공개 권한 제어
    - 페이지네이션 지원
    """
    media_service = MediaService(db)
    
    result = await media_service.get_media_list(
        target_type=target_type,
        target_id=target_id,
        media_type=media_type,
        user_id=current_user.id if current_user else None,
        only_public=only_public,
        page=page,
        page_size=page_size
    )
    
    # 미디어 응답 변환
    media_responses = []
    for media in result["media"]:
        media_response = MediaResponse(
            id=media.id,
            target_type=media.target_type,
            target_id=media.target_id,
            original_name=media.original_name,
            file_path=media.file_path,
            file_size=media.file_size,
            mime_type=media.mime_type,
            type=media.type,
            width=media.width,
            height=media.height,
            duration=media.duration,
            is_public=media.is_public,
            alt_text=media.alt_text,
            created_at=media.created_at,
            updated_at=media.updated_at,
            file_extension=media.file_extension,
            is_image=media.is_image,
            is_video=media.is_video,
            file_size_mb=media.file_size_mb,
            download_url=media_service.get_download_url(media),
            thumbnail_url=media_service.get_thumbnail_url(media)
        )
        media_responses.append(media_response)
    
    return MediaListResponse(
        media=media_responses,
        total_count=result["total_count"],
        page=result["page"],
        page_size=result["page_size"],
        total_pages=result["total_pages"]
    )


@router.get("/{media_id}", response_model=MediaResponse)
async def get_media_by_id(
    media_id: int,
    current_user: Optional[User] = Depends(get_current_user_optional),
    db: AsyncSession = Depends(get_db)
):
    """미디어 상세 정보 조회"""
    media_service = MediaService(db)
    
    media = await media_service.get_media_by_id(
        media_id, 
        current_user.id if current_user else None
    )
    
    if not media:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Media not found"
        )
    
    return MediaResponse(
        id=media.id,
        target_type=media.target_type,
        target_id=media.target_id,
        original_name=media.original_name,
        file_path=media.file_path,
        file_size=media.file_size,
        mime_type=media.mime_type,
        type=media.type,
        width=media.width,
        height=media.height,
        duration=media.duration,
        is_public=media.is_public,
        alt_text=media.alt_text,
        created_at=media.created_at,
        updated_at=media.updated_at,
        file_extension=media.file_extension,
        is_image=media.is_image,
        is_video=media.is_video,
        file_size_mb=media.file_size_mb,
        download_url=media_service.get_download_url(media),
        thumbnail_url=media_service.get_thumbnail_url(media)
    )


@router.patch("/{media_id}", response_model=MediaResponse)
async def update_media(
    media_id: int,
    update_data: MediaUpdateRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """미디어 정보 수정"""
    media_service = MediaService(db)
    
    media = await media_service.update_media(
        media_id=media_id,
        user_id=current_user.id,
        alt_text=update_data.alt_text,
        is_public=update_data.is_public
    )
    
    if not media:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Media not found"
        )
    
    return MediaResponse(
        id=media.id,
        target_type=media.target_type,
        target_id=media.target_id,
        original_name=media.original_name,
        file_path=media.file_path,
        file_size=media.file_size,
        mime_type=media.mime_type,
        type=media.type,
        width=media.width,
        height=media.height,
        duration=media.duration,
        is_public=media.is_public,
        alt_text=media.alt_text,
        created_at=media.created_at,
        updated_at=media.updated_at,
        file_extension=media.file_extension,
        is_image=media.is_image,
        is_video=media.is_video,
        file_size_mb=media.file_size_mb,
        download_url=media_service.get_download_url(media),
        thumbnail_url=media_service.get_thumbnail_url(media)
    )


@router.delete("/{media_id}")
async def delete_media(
    media_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """미디어 삭제"""
    media_service = MediaService(db)
    
    success = await media_service.delete_media(media_id, current_user.id)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Media not found"
        )
    
    return {"success": True, "message": "Media deleted successfully"}


@router.post("/bulk-delete")
async def bulk_delete_media(
    delete_request: MediaBulkDeleteRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """미디어 일괄 삭제"""
    media_service = MediaService(db)
    
    result = await media_service.bulk_delete_media(
        delete_request.media_ids, 
        current_user.id
    )
    
    return {
        "success": True,
        "deleted_count": result["deleted_count"],
        "failed_count": result["failed_count"],
        "failed_ids": result["failed_ids"]
    }


@router.get("/{media_id}/download")
async def download_media(
    media_id: int,
    current_user: Optional[User] = Depends(get_current_user_optional),
    db: AsyncSession = Depends(get_db)
):
    """미디어 파일 다운로드"""
    media_service = MediaService(db)
    
    media = await media_service.get_media_by_id(
        media_id, 
        current_user.id if current_user else None
    )
    
    if not media:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Media not found"
        )
    
    file_path = Path(media.file_path)
    if not file_path.exists():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="File not found on disk"
        )
    
    return FileResponse(
        path=file_path,
        filename=media.original_name,
        media_type=media.mime_type
    )


@router.get("/{media_id}/thumbnail")
async def get_thumbnail(
    media_id: int,
    current_user: Optional[User] = Depends(get_current_user_optional),
    db: AsyncSession = Depends(get_db)
):
    """이미지 썸네일 조회"""
    media_service = MediaService(db)
    
    media = await media_service.get_media_by_id(
        media_id, 
        current_user.id if current_user else None
    )
    
    if not media:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Media not found"
        )
    
    if not media.is_image:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Thumbnail is only available for images"
        )
    
    # 썸네일 경로 계산
    file_path = Path(media.file_path)
    thumbnail_path = file_path.parent / f"thumb_{file_path.name}"
    
    if not thumbnail_path.exists():
        # 썸네일이 없으면 원본 이미지 반환
        thumbnail_path = file_path
    
    if not thumbnail_path.exists():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Thumbnail not found"
        )
    
    return FileResponse(
        path=thumbnail_path,
        media_type="image/jpeg"
    )


@router.get("/stats/storage", response_model=MediaStorageStats)
async def get_storage_stats(
    current_user: Optional[User] = Depends(get_current_user_optional),
    db: AsyncSession = Depends(get_db)
):
    """저장소 통계 조회"""
    media_service = MediaService(db)
    
    stats = await media_service.get_storage_stats(
        current_user.id if current_user else None
    )
    
    return MediaStorageStats(**stats)