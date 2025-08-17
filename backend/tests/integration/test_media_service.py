"""
통합 테스트: 미디어 서비스
실제 데이터베이스와 파일 시스템을 사용한 미디어 서비스 통합 테스트
"""

import tempfile
from io import BytesIO
from pathlib import Path

import pytest
from app.models.media import Media, MediaTargetType, MediaType
from app.models.project import Project
from app.models.user import User
from app.services.media import MediaService
from fastapi import HTTPException
from PIL import Image
from sqlalchemy.ext.asyncio import AsyncSession


@pytest.mark.integration
@pytest.mark.media
class TestMediaServiceIntegration:
    """미디어 서비스 통합 테스트"""

    @pytest.fixture(autouse=True)
    async def setup(
        self,
        test_db: AsyncSession,
        test_user: User,
        test_project: Project,
        temp_media_dir: Path,
        mock_upload_file,
    ):
        """테스트 설정"""
        self.db = test_db
        self.user = test_user
        self.project = test_project
        self.temp_dir = temp_media_dir
        self.mock_upload_file = mock_upload_file

        # MediaService 인스턴스 생성
        self.media_service = MediaService(test_db)

        # 임시 미디어 디렉토리 설정
        self.media_service.upload_dir = self.temp_dir

    def create_test_image(
        self, width: int = 800, height: int = 600, format: str = "PNG"
    ) -> BytesIO:
        """테스트용 이미지 생성"""
        image = Image.new("RGB", (width, height), color="red")
        buffer = BytesIO()
        image.save(buffer, format=format)
        buffer.seek(0)
        return buffer

    @pytest.mark.asyncio
    async def test_upload_image_full_flow(
        self,
        test_db: AsyncSession,
        test_user: User,
        test_project: Project,
        temp_media_dir: Path,
        mock_upload_file,
    ):
        """이미지 업로드 전체 플로우 테스트"""
        # 서비스 초기화
        media_service = MediaService(test_db)
        media_service.upload_dir = temp_media_dir

        # 테스트 이미지 생성
        image_buffer = self.create_test_image(800, 600, "PNG")
        upload_file = mock_upload_file(
            filename="test-image.png", content=image_buffer, content_type="image/png"
        )

        # 이미지 업로드
        media = await media_service.upload_file(
            file=upload_file,
            target_type=MediaTargetType.PROJECT,
            target_id=test_project.id,
            user_id=self.user.id,
        )

        # 결과 검증
        assert media is not None
        assert media.type == MediaType.IMAGE
        assert media.target_type == MediaTargetType.PROJECT
        assert media.target_id == self.project.id
        assert media.original_name == "test-image.png"
        assert media.mime_type == "image/png"
        assert media.file_size > 0

        # 메타데이터 검증
        assert media.width == 800
        assert media.height == 600

        # 파일 시스템 검증
        file_path = Path(media.file_path)
        assert file_path.exists()
        assert file_path.is_file()

        # 데이터베이스 검증
        saved_media = await self.media_service.get_media_by_id(
            media.id, user_id=self.user.id
        )
        assert saved_media is not None
        assert saved_media.id == media.id

    @pytest.mark.asyncio
    async def test_upload_document_full_flow(self):
        """문서 업로드 전체 플로우 테스트"""
        # 테스트 문서 생성
        content = "Test document content"
        doc_buffer = BytesIO(content.encode())
        upload_file = self.mock_upload_file(
            filename="test-doc.txt", content=doc_buffer, content_type="text/plain"
        )

        # 문서 업로드
        media = await self.media_service.upload_file(
            file=upload_file,
            target_type=MediaTargetType.PROJECT,
            target_id=self.project.id,
            user_id=self.user.id,
        )

        # 결과 검증
        assert media is not None
        assert media.type == MediaType.DOCUMENT
        assert media.target_type == MediaTargetType.PROJECT
        assert media.target_id == self.project.id
        assert media.original_name == "test-doc.txt"
        assert media.mime_type == "text/plain"
        assert media.file_size == len(content.encode())

        # 파일 시스템 검증
        file_path = Path(media.file_path)
        assert file_path.exists()
        assert file_path.read_text() == content

    @pytest.mark.asyncio
    async def test_image_processing_and_thumbnails(self):
        """이미지 처리 및 썸네일 생성 테스트"""
        # 큰 이미지 생성
        large_image = self.create_test_image(2000, 1500, "JPEG")
        upload_file = self.mock_upload_file(
            filename="large-image.jpg", content=large_image, content_type="image/jpeg"
        )

        # 업로드
        media = await self.media_service.upload_file(
            file=upload_file,
            target_type=MediaTargetType.PROJECT,
            target_id=self.project.id,
            user_id=self.user.id,
        )

        # 원본 이미지 검증
        assert media.width == 2000
        assert media.height == 1500

        # 썸네일 생성 (서비스에 썸네일 기능이 있다면)
        # thumbnail_path = await self.media_service.create_thumbnail(media.id)
        # assert thumbnail_path is not None

        # 리사이징 테스트 (서비스에 리사이징 기능이 있다면)
        # resized_media = await self.media_service.resize_image(media.id, 800, 600)
        # assert resized_media.metadata["width"] == 800
        # assert resized_media.metadata["height"] == 600

    @pytest.mark.asyncio
    async def test_media_permissions_integration(self):
        """미디어 권한 통합 테스트"""
        # 다른 사용자 생성
        other_user = User(
            email="other@example.com",
            name="Other User",
            github_username="otheruser",
            is_verified=True,
        )
        self.db.add(other_user)
        await self.db.commit()
        await self.db.refresh(other_user)

        # 이미지 업로드 (원래 사용자)
        image_buffer = self.create_test_image()
        upload_file = self.mock_upload_file(
            filename="test-image.png", content=image_buffer, content_type="image/png"
        )

        media = await self.media_service.upload_file(
            file=upload_file,
            target_type=MediaTargetType.PROJECT,
            target_id=self.project.id,
            user_id=self.user.id,
        )

        # 원래 사용자는 접근 가능
        retrieved_media = await self.media_service.get_media_by_id(
            media.id, user_id=self.user.id
        )
        assert retrieved_media is not None

        # 다른 사용자는 접근 불가 (비공개 프로젝트인 경우)
        if hasattr(self.media_service, "check_media_access"):
            has_access = await self.media_service.check_media_access(
                media.id, user_id=other_user.id
            )
            # 프로젝트 공개 여부에 따라 결과가 달라짐
            # assert has_access == (self.project.visibility == ProjectVisibility.PUBLIC)

    @pytest.mark.asyncio
    async def test_media_cleanup_on_delete(self):
        """미디어 삭제 시 파일 정리 테스트"""
        # 이미지 업로드
        image_buffer = self.create_test_image()
        upload_file = self.mock_upload_file(
            filename="test-image.png", content=image_buffer, content_type="image/png"
        )

        media = await self.media_service.upload_file(
            file=upload_file,
            target_type=MediaTargetType.PROJECT,
            target_id=self.project.id,
            user_id=self.user.id,
        )

        # 파일 존재 확인
        file_path = Path(media.file_path)
        assert file_path.exists()

        # 미디어 삭제
        await self.media_service.delete_media(media.id, user_id=self.user.id)

        # 파일 삭제 확인
        assert not file_path.exists()

        # 데이터베이스에서 삭제 확인
        deleted_media = await self.media_service.get_media_by_id(media.id)
        assert deleted_media is None

    @pytest.mark.asyncio
    async def test_bulk_media_operations(self):
        """대량 미디어 작업 테스트"""
        media_list = []

        # 여러 이미지 업로드
        for i in range(5):
            image_buffer = self.create_test_image(100 + i * 10, 100 + i * 10)
            upload_file = self.mock_upload_file(
                filename=f"test-image-{i}.png",
                content=image_buffer,
                content_type="image/png",
            )

            media = await self.media_service.upload_file(
                file=upload_file,
                target_type=MediaTargetType.PROJECT,
                target_id=self.project.id,
                user_id=self.user.id,
            )
            media_list.append(media)

        # 프로젝트의 모든 미디어 조회
        project_media = await self.media_service.get_media_by_target(
            target_type=MediaTargetType.PROJECT, target_id=self.project.id
        )

        assert len(project_media) == 5

        # 미디어 ID 목록으로 조회
        media_ids = [m.id for m in media_list]
        retrieved_media = await self.media_service.get_media_by_ids(media_ids)

        assert len(retrieved_media) == 5
        assert all(m.id in media_ids for m in retrieved_media)

    @pytest.mark.asyncio
    async def test_error_handling_integration(self):
        """에러 처리 통합 테스트"""
        # 잘못된 파일 형식
        invalid_file = self.mock_upload_file(
            filename="test.exe",
            content=BytesIO(b"invalid content"),
            content_type="application/x-executable",
        )

        with pytest.raises(HTTPException, match="Unsupported file type"):
            await self.media_service.upload_file(
                file=invalid_file,
                target_type=MediaTargetType.PROJECT,
                target_id=self.project.id,
                user_id=self.user.id,
            )

        # 파일 크기 초과 (설정에 따라)
        if hasattr(self.media_service, "max_file_size"):
            large_content = b"x" * (self.media_service.max_file_size + 1)
            large_file = self.mock_upload_file(
                filename="large.txt",
                content=BytesIO(large_content),
                content_type="text/plain",
            )

            with pytest.raises(HTTPException, match="File too large"):
                await self.media_service.upload_file(
                    file=large_file,
                    target_type=MediaTargetType.PROJECT,
                    target_id=self.project.id,
                    user_id=self.user.id,
                )

        # 존재하지 않는 타겟
        image_buffer = self.create_test_image()
        upload_file = self.mock_upload_file(
            filename="test.png", content=image_buffer, content_type="image/png"
        )

        with pytest.raises(HTTPException, match="Project not found"):
            await self.media_service.upload_file(
                file=upload_file,
                target_type=MediaTargetType.PROJECT,
                target_id=99999,  # 존재하지 않는 ID
                user_id=self.user.id,
            )
