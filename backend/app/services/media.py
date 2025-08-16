"""
미디어 서비스
파일 업로드, 이미지 처리, 저장소 관리
"""

import os
import uuid
import mimetypes
import aiofiles
from pathlib import Path
from typing import Optional, List, Dict, Any, Tuple
from datetime import datetime, timezone
import hashlib
from io import BytesIO

from fastapi import HTTPException, status, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_, func, desc, delete
from sqlalchemy.orm import selectinload
from PIL import Image
import pillow_heif

from app.models.media import Media, MediaType, MediaTargetType
from app.models.project import Project, ProjectVisibility, ProjectStatus
from app.models.note import Note
from app.models.user import User
from app.core.config import settings


# Pillow에 HEIF 지원 추가
pillow_heif.register_heif_opener()


class MediaService:
    """미디어 관련 비즈니스 로직"""
    
    # 파일 크기 제한 (bytes)
    MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB
    MAX_IMAGE_SIZE = 10 * 1024 * 1024  # 10MB
    MAX_VIDEO_SIZE = 100 * 1024 * 1024  # 100MB
    
    # 허용된 MIME 타입
    ALLOWED_IMAGE_TYPES = {
        "image/jpeg", "image/png", "image/gif", "image/webp", 
        "image/svg+xml", "image/heic", "image/heif"
    }
    ALLOWED_VIDEO_TYPES = {
        "video/mp4", "video/webm", "video/ogg", "video/quicktime", 
        "video/x-msvideo", "video/avi"  # AVI 지원 추가
    }
    ALLOWED_DOCUMENT_TYPES = {
        "application/pdf", "text/plain", "text/markdown",
        "application/msword", "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    }
    ALLOWED_ARCHIVE_TYPES = {
        "application/zip", "application/x-tar", "application/gzip",
        "application/vnd.rar", "application/x-rar-compressed",  # RAR 지원 추가
        "application/x-gzip"  # 추가 gzip 타입
    }
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self.upload_dir = Path(settings.MEDIA_ROOT)
        self.upload_dir.mkdir(parents=True, exist_ok=True)
    
    async def upload_file(
        self,
        file: UploadFile,
        target_type: MediaTargetType,
        target_id: int,
        user_id: str,
        alt_text: Optional[str] = None,
        is_public: bool = False,
        process_image: bool = True
    ) -> Media:
        """
        파일 업로드 및 저장
        
        Args:
            file: 업로드할 파일
            target_type: 대상 타입 (project/note)
            target_id: 대상 ID
            user_id: 업로드하는 사용자 ID
            alt_text: 대체 텍스트
            is_public: 공개 여부
            process_image: 이미지 처리 여부
            
        Returns:
            Media: 생성된 미디어 객체
        """
        start_time = datetime.now()
        
        # 1. 권한 검사
        await self._check_upload_permission(target_type, target_id, user_id)
        
        # 2. 파일 유효성 검사
        await self._validate_file(file)
        
        # 3. 파일 정보 추출
        file_info = await self._extract_file_info(file)
        
        # 4. 파일 저장
        file_path, file_name = await self._save_file(file, file_info)
        
        # 5. 이미지 처리 및 메타데이터 추출
        media_metadata = {}
        if file_info["media_type"] == MediaType.IMAGE and process_image:
            media_metadata = await self._process_image(file_path)
        elif file_info["media_type"] == MediaType.VIDEO:
            media_metadata = await self._extract_video_metadata(file_path)
        
        # 6. 데이터베이스에 저장
        media = Media(
            target_type=target_type,
            target_id=target_id,
            original_name=file.filename,
            file_name=file_name,
            file_path=str(file_path),
            file_size=file_info["file_size"],
            mime_type=file_info["mime_type"],
            type=file_info["media_type"],
            width=media_metadata.get("width"),
            height=media_metadata.get("height"),
            duration=media_metadata.get("duration"),
            is_public=is_public,
            alt_text=alt_text,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc)
        )
        
        self.db.add(media)
        await self.db.commit()
        await self.db.refresh(media)
        
        return media
    
    async def get_media_by_id(self, media_id: int, user_id: Optional[str] = None) -> Optional[Media]:
        """미디어 ID로 조회"""
        stmt = select(Media).where(Media.id == media_id)
        result = await self.db.execute(stmt)
        media = result.scalar_one_or_none()
        
        if not media:
            return None
        
        # 권한 검사
        if not await self._check_media_access_permission(media, user_id):
            return None
        
        return media
    
    async def get_media_list(
        self,
        target_type: Optional[MediaTargetType] = None,
        target_id: Optional[int] = None,
        media_type: Optional[MediaType] = None,
        user_id: Optional[str] = None,
        only_public: bool = True,
        page: int = 1,
        page_size: int = 20
    ) -> Dict[str, Any]:
        """
        미디어 목록 조회
        
        Args:
            target_type: 대상 타입 필터
            target_id: 대상 ID 필터
            media_type: 미디어 타입 필터
            user_id: 사용자 ID (권한 확인용)
            only_public: 공개 파일만 조회할지 여부
            page: 페이지 번호
            page_size: 페이지 크기
            
        Returns:
            Dict: 미디어 목록과 메타정보
        """
        # 기본 쿼리
        stmt = select(Media)
        count_stmt = select(func.count(Media.id))
        
        # 필터 조건
        filters = []
        
        if target_type:
            filters.append(Media.target_type == target_type)
        
        if target_id:
            filters.append(Media.target_id == target_id)
        
        if media_type:
            filters.append(Media.type == media_type)
        
        # 권한 필터
        if only_public and not user_id:
            filters.append(Media.is_public == True)
        elif user_id:
            # 사용자별 접근 권한 확인
            access_filter = await self._build_access_filter(user_id, only_public)
            if access_filter is not None:
                filters.append(access_filter)
        
        # 필터 적용
        if filters:
            stmt = stmt.where(and_(*filters))
            count_stmt = count_stmt.where(and_(*filters))
        
        # 정렬 (최신순)
        stmt = stmt.order_by(desc(Media.created_at))
        
        # 페이지네이션
        offset = (page - 1) * page_size
        stmt = stmt.offset(offset).limit(page_size)
        
        # 실행
        count_result = await self.db.execute(count_stmt)
        total_count = count_result.scalar()
        
        result = await self.db.execute(stmt)
        media_list = result.scalars().all()
        
        # 추가 정보 계산
        total_pages = (total_count + page_size - 1) // page_size
        
        return {
            "media": media_list,
            "total_count": total_count,
            "page": page,
            "page_size": page_size,
            "total_pages": total_pages
        }
    
    async def update_media(
        self,
        media_id: int,
        user_id: str,
        alt_text: Optional[str] = None,
        is_public: Optional[bool] = None
    ) -> Optional[Media]:
        """미디어 정보 수정"""
        # 미디어 조회 및 권한 확인
        media = await self.get_media_by_id(media_id, user_id)
        if not media:
            return None
        
        # 대상 소유권 확인
        if not await self._check_target_ownership(media.target_type, media.target_id, user_id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Permission denied"
            )
        
        # 정보 업데이트
        if alt_text is not None:
            media.alt_text = alt_text
        if is_public is not None:
            media.is_public = is_public
        
        media.updated_at = datetime.now(timezone.utc)
        
        await self.db.commit()
        await self.db.refresh(media)
        
        return media
    
    async def delete_media(self, media_id: int, user_id: str) -> bool:
        """미디어 삭제"""
        # 미디어 조회 및 권한 확인
        media = await self.get_media_by_id(media_id, user_id)
        if not media:
            return False
        
        # 대상 소유권 확인
        if not await self._check_target_ownership(media.target_type, media.target_id, user_id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Permission denied"
            )
        
        # 파일 시스템에서 삭제
        try:
            file_path = Path(media.file_path)
            if file_path.exists():
                file_path.unlink()
            
            # 썸네일이 있다면 삭제
            thumbnail_path = self._get_thumbnail_path(file_path)
            if thumbnail_path.exists():
                thumbnail_path.unlink()
        except Exception:
            # 파일 삭제 실패해도 DB에서는 삭제
            pass
        
        # 데이터베이스에서 삭제
        await self.db.delete(media)
        await self.db.commit()
        
        return True
    
    async def bulk_delete_media(self, media_ids: List[int], user_id: str) -> Dict[str, Any]:
        """미디어 일괄 삭제"""
        deleted_count = 0
        failed_ids = []
        
        for media_id in media_ids:
            try:
                success = await self.delete_media(media_id, user_id)
                if success:
                    deleted_count += 1
                else:
                    failed_ids.append(media_id)
            except Exception:
                failed_ids.append(media_id)
        
        return {
            "deleted_count": deleted_count,
            "failed_count": len(failed_ids),
            "failed_ids": failed_ids
        }
    
    async def get_storage_stats(self, user_id: Optional[str] = None) -> Dict[str, Any]:
        """저장소 통계 조회"""
        # 기본 필터 조건
        filters = []
        
        # 사용자별 필터
        if user_id:
            # 사용자가 접근 가능한 미디어만
            access_filter = await self._build_access_filter(user_id, only_public=False)
            if access_filter is not None:
                filters.append(access_filter)
        else:
            # 공개 미디어만
            filters.append(Media.is_public == True)
        
        # 통계 쿼리들
        total_count_stmt = select(func.count(Media.id))
        total_size_stmt = select(func.sum(Media.file_size))
        
        type_stats_stmt = select(
            Media.type,
            func.count(Media.id).label('count')
        ).group_by(Media.type)
        
        visibility_stats_stmt = select(
            Media.is_public,
            func.count(Media.id).label('count')
        ).group_by(Media.is_public)
        
        # 필터 적용
        if filters:
            filter_condition = and_(*filters) if len(filters) > 1 else filters[0]
            total_count_stmt = total_count_stmt.where(filter_condition)
            total_size_stmt = total_size_stmt.where(filter_condition)
            type_stats_stmt = type_stats_stmt.where(filter_condition)
            visibility_stats_stmt = visibility_stats_stmt.where(filter_condition)
        
        # 실행
        total_count_result = await self.db.execute(total_count_stmt)
        total_count = total_count_result.scalar() or 0
        
        total_size_result = await self.db.execute(total_size_stmt)
        total_size = total_size_result.scalar() or 0
        
        type_stats_result = await self.db.execute(type_stats_stmt)
        type_stats = {row.type: row.count for row in type_stats_result}
        
        visibility_stats_result = await self.db.execute(visibility_stats_stmt)
        visibility_stats = {row.is_public: row.count for row in visibility_stats_result}
        
        return {
            "total_files": total_count,
            "total_size": total_size,
            "total_size_mb": round(total_size / (1024 * 1024), 2),
            "by_type": {
                "images": type_stats.get(MediaType.IMAGE, 0),
                "videos": type_stats.get(MediaType.VIDEO, 0),
                "documents": type_stats.get(MediaType.DOCUMENT, 0),
                "archives": type_stats.get(MediaType.ARCHIVE, 0)
            }
        }
    
    def get_download_url(self, media: Media) -> str:
        """다운로드 URL 생성"""
        return f"/api/v1/media/{media.id}/download"
    
    def get_thumbnail_url(self, media: Media) -> Optional[str]:
        """썸네일 URL 생성"""
        if media.is_image:
            return f"/api/v1/media/{media.id}/thumbnail"
        return None
    
    async def _check_upload_permission(
        self, 
        target_type: MediaTargetType, 
        target_id: int, 
        user_id: str
    ) -> None:
        """업로드 권한 확인"""
        if target_type == MediaTargetType.PROJECT:
            stmt = select(Project).where(Project.id == target_id)
            result = await self.db.execute(stmt)
            project = result.scalar_one_or_none()
            
            if not project:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Project not found"
                )
            
            if project.owner_id != user_id:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Permission denied"
                )
        
        elif target_type == MediaTargetType.NOTE:
            stmt = select(Note).join(Project).where(Note.id == target_id)
            result = await self.db.execute(stmt)
            note = result.scalar_one_or_none()
            
            if not note:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Note not found"
                )
            
            if note.project.owner_id != user_id:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Permission denied"
                )
    
    async def _check_target_ownership(
        self, 
        target_type: MediaTargetType, 
        target_id: int, 
        user_id: str
    ) -> bool:
        """대상 소유권 확인"""
        try:
            await self._check_upload_permission(target_type, target_id, user_id)
            return True
        except HTTPException:
            return False
    
    async def _check_media_access_permission(self, media: Media, user_id: Optional[str]) -> bool:
        """미디어 접근 권한 확인"""
        # 공개 미디어는 모든 사용자 접근 가능
        if media.is_public:
            return True
        
        # 로그인하지 않은 사용자는 비공개 미디어 접근 불가
        if not user_id:
            return False
        
        # 소유권 확인
        return await self._check_target_ownership(media.target_type, media.target_id, user_id)
    
    async def _build_access_filter(self, user_id: str, only_public: bool):
        """접근 권한 필터 생성"""
        if only_public:
            return Media.is_public == True
        
        # 사용자가 접근 가능한 미디어 필터
        # 1. 공개 미디어
        # 2. 사용자 소유 프로젝트/노트의 미디어
        
        # 사용자 소유 프로젝트 서브쿼리
        user_projects = select(Project.id).where(Project.owner_id == user_id)
        
        # 사용자 소유 노트 서브쿼리
        user_notes = select(Note.id).join(Project).where(Project.owner_id == user_id)
        
        access_filter = or_(
            Media.is_public == True,
            and_(
                Media.target_type == MediaTargetType.PROJECT,
                Media.target_id.in_(user_projects)
            ),
            and_(
                Media.target_type == MediaTargetType.NOTE,
                Media.target_id.in_(user_notes)
            )
        )
        
        return access_filter
    
    async def _validate_file(self, file: UploadFile) -> None:
        """파일 유효성 검사"""
        # 파일명 확인
        if not file.filename:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Filename is required"
            )
        
        # 파일 크기 확인
        content = await file.read()
        file_size = len(content)
        await file.seek(0)  # 파일 포인터 리셋
        
        if file_size == 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="File is empty"
            )
        
        if file_size > self.MAX_FILE_SIZE:
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail=f"File too large. Maximum size: {self.MAX_FILE_SIZE // (1024 * 1024)}MB"
            )
        
        # MIME 타입 확인
        mime_type = file.content_type or mimetypes.guess_type(file.filename)[0]
        if not mime_type:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Could not determine file type"
            )
        
        allowed_types = (
            self.ALLOWED_IMAGE_TYPES | 
            self.ALLOWED_VIDEO_TYPES | 
            self.ALLOWED_DOCUMENT_TYPES | 
            self.ALLOWED_ARCHIVE_TYPES
        )
        
        if mime_type not in allowed_types:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Unsupported file type: {mime_type}"
            )
        
        # 타입별 크기 제한
        if mime_type in self.ALLOWED_IMAGE_TYPES and file_size > self.MAX_IMAGE_SIZE:
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail=f"Image too large. Maximum size: {self.MAX_IMAGE_SIZE // (1024 * 1024)}MB"
            )
        
        if mime_type in self.ALLOWED_VIDEO_TYPES and file_size > self.MAX_VIDEO_SIZE:
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail=f"Video too large. Maximum size: {self.MAX_VIDEO_SIZE // (1024 * 1024)}MB"
            )
    
    async def _extract_file_info(self, file: UploadFile) -> Dict[str, Any]:
        """파일 정보 추출"""
        content = await file.read()
        await file.seek(0)
        
        mime_type = file.content_type or mimetypes.guess_type(file.filename)[0]
        
        # 미디어 타입 결정
        if mime_type in self.ALLOWED_IMAGE_TYPES:
            media_type = MediaType.IMAGE
        elif mime_type in self.ALLOWED_VIDEO_TYPES:
            media_type = MediaType.VIDEO
        elif mime_type in self.ALLOWED_DOCUMENT_TYPES:
            media_type = MediaType.DOCUMENT
        elif mime_type in self.ALLOWED_ARCHIVE_TYPES:
            media_type = MediaType.ARCHIVE
        else:
            media_type = MediaType.DOCUMENT  # 기본값
        
        return {
            "content": content,
            "file_size": len(content),
            "mime_type": mime_type,
            "media_type": media_type
        }
    
    async def _save_file(self, file: UploadFile, file_info: Dict[str, Any]) -> Tuple[Path, str]:
        """파일 저장"""
        # 고유 파일명 생성
        file_hash = hashlib.md5(file_info["content"]).hexdigest()[:8]
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        file_extension = Path(file.filename).suffix.lower()
        
        file_name = f"{timestamp}_{file_hash}{file_extension}"
        
        # 년/월 기준 디렉토리 생성
        now = datetime.now()
        upload_path = self.upload_dir / str(now.year) / f"{now.month:02d}"
        upload_path.mkdir(parents=True, exist_ok=True)
        
        file_path = upload_path / file_name
        
        # 파일 저장
        async with aiofiles.open(file_path, 'wb') as f:
            await f.write(file_info["content"])
        
        return file_path, file_name
    
    async def _process_image(self, file_path: Path) -> Dict[str, Any]:
        """이미지 처리 및 메타데이터 추출"""
        try:
            with Image.open(file_path) as img:
                width, height = img.size
                
                # 썸네일 생성
                thumbnail_path = self._get_thumbnail_path(file_path)
                thumbnail_size = (300, 300)
                
                img.thumbnail(thumbnail_size, Image.Resampling.LANCZOS)
                img.save(thumbnail_path, optimize=True, quality=85)
                
                return {
                    "width": width,
                    "height": height
                }
        except Exception:
            return {}
    
    def _get_thumbnail_path(self, file_path: Path) -> Path:
        """썸네일 경로 생성"""
        return file_path.parent / f"thumb_{file_path.name}"
    
    async def _extract_video_metadata(self, file_path: Path) -> Dict[str, Any]:
        """비디오 메타데이터 추출 (기본 구현)"""
        # 실제로는 ffprobe 등을 사용하여 비디오 정보 추출
        # 현재는 기본값만 반환
        return {
            "duration": None,
            "width": None,
            "height": None
        }
    
    # ========== Private helper methods for unit testing ==========
    
    def _detect_file_type(self, filename: str, mime_type: str) -> MediaType:
        """파일 타입 감지 (단위 테스트용)"""
        if mime_type in self.ALLOWED_IMAGE_TYPES:
            return MediaType.IMAGE
        elif mime_type in self.ALLOWED_VIDEO_TYPES:
            return MediaType.VIDEO
        elif mime_type in self.ALLOWED_DOCUMENT_TYPES:
            return MediaType.DOCUMENT
        elif mime_type in self.ALLOWED_ARCHIVE_TYPES:
            return MediaType.ARCHIVE
        else:
            return MediaType.DOCUMENT  # 기본값
    
    def _get_image_dimensions(self, image_buffer) -> Tuple[int, int]:
        """이미지 크기 계산 (단위 테스트용)"""
        try:
            with Image.open(image_buffer) as img:
                return img.size
        except Exception:
            return (0, 0)
    
    def _get_file_extension(self, filename: str) -> str:
        """파일 확장자 추출 (단위 테스트용)"""
        return Path(filename).suffix.lower()
    
    async def _create_thumbnail(self, image_buffer) -> BytesIO:
        """썸네일 생성 (단위 테스트용)"""
        try:
            with Image.open(image_buffer) as img:
                img.thumbnail((300, 300), Image.Resampling.LANCZOS)
                buffer = BytesIO()
                
                # 투명도가 있는 이미지는 배경을 흰색으로 채우고 JPEG로 변환
                if img.mode in ('RGBA', 'LA', 'P'):
                    # 새 RGB 이미지 생성 (흰색 배경)
                    rgb_img = Image.new('RGB', img.size, (255, 255, 255))
                    rgb_img.paste(img, mask=img.split()[-1] if img.mode == 'RGBA' else None)
                    rgb_img.save(buffer, format='JPEG', optimize=True, quality=85)
                else:
                    img.save(buffer, format='JPEG', optimize=True, quality=85)
                    
                buffer.seek(0)  # 중요: 버퍼 위치를 처음으로 리셋
                return buffer
        except Exception:
            # 에러 발생시 빈 버퍼 반환
            error_buffer = BytesIO()
            error_buffer.seek(0)
            return error_buffer
    
    def _generate_safe_filename(self, filename: str) -> str:
        """안전한 파일명 생성 (단위 테스트용)"""
        import re
        from pathlib import Path
        
        # 파일명과 확장자 분리
        path = Path(filename)
        name = path.stem
        extension = path.suffix
        
        # 특수문자 제거 및 안전한 파일명으로 변환
        safe_name = re.sub(r'[^\w\.-]', '_', name)
        
        # UUID 추가로 고유성 보장
        unique_id = str(uuid.uuid4())[:8]
        
        return f"{safe_name}_{unique_id}{extension}"
    
    async def _process_image(self, image_buffer, filename: str) -> Tuple[BytesIO, Dict[str, Any]]:
        """이미지 처리 (단위 테스트용) - 리사이즈 및 최적화"""
        try:
            from io import BytesIO
            with Image.open(image_buffer) as img:
                original_width, original_height = img.size
                
                # 최대 크기 제한 (1920x1080)
                max_width, max_height = 1920, 1080
                
                # 비율 유지하며 리사이즈
                if original_width > max_width or original_height > max_height:
                    img.thumbnail((max_width, max_height), Image.Resampling.LANCZOS)
                
                # 최적화된 형식으로 저장 (JPEG)
                output_buffer = BytesIO()
                if img.mode in ('RGBA', 'LA', 'P'):
                    # 투명도가 있는 이미지는 PNG로 유지
                    img.save(output_buffer, format='PNG', optimize=True)
                    format_used = "PNG"
                else:
                    # RGB 이미지는 JPEG로 변환
                    img.save(output_buffer, format='JPEG', optimize=True, quality=85)
                    format_used = "JPEG"
                
                processed_width, processed_height = img.size
                output_buffer.seek(0)  # 중요: 버퍼 위치를 처음으로 리셋
                
                metadata = {
                    "width": processed_width,
                    "height": processed_height,
                    "format": format_used,
                    "original_width": original_width,
                    "original_height": original_height
                }
                
                return output_buffer, metadata
                
        except Exception as e:
            # 에러 발생시 원본 반환
            image_buffer.seek(0)
            error_buffer = BytesIO(image_buffer.read())
            error_buffer.seek(0)
            return error_buffer, {
                "width": 0,
                "height": 0,
                "format": "UNKNOWN",
                "original_width": 0,
                "original_height": 0,
                "error": str(e)
            }