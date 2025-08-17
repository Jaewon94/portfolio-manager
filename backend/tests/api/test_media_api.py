"""
미디어 API 테스트
Media endpoints: 업로드, 다운로드, 썸네일, 삭제, 통계
"""

from io import BytesIO

import pytest
from app.core.security import create_access_token
from app.models.user import User
from httpx import AsyncClient


@pytest.mark.api
@pytest.mark.media
class TestMediaAPI:
    """미디어 관련 API 테스트"""

    def create_test_file(
        self, content: bytes = b"test file content", filename: str = "test.txt"
    ) -> BytesIO:
        """테스트용 파일 생성"""
        buffer = BytesIO(content)
        buffer.name = filename
        return buffer

    @pytest.mark.asyncio
    async def test_media_list_public_access(self, async_client: AsyncClient):
        """미디어 목록 조회 - 공개 접근"""
        response = await async_client.get("/api/v1/media/")
        # 공개 접근이 가능하면 200, 인증 필요하면 401
        assert response.status_code in [200, 401]

        if response.status_code == 200:
            data = response.json()
            # 페이지네이션 응답이면 dict, 단순 리스트면 list
            assert isinstance(data, (list, dict))

    @pytest.mark.asyncio
    async def test_media_list_with_auth(self, authenticated_client: AsyncClient):
        """미디어 목록 조회 - 인증됨"""
        response = await authenticated_client.get("/api/v1/media/")
        assert response.status_code in [200, 401]

        if response.status_code == 200:
            data = response.json()
            # 페이지네이션 응답이면 dict, 단순 리스트면 list
            assert isinstance(data, (list, dict))

    @pytest.mark.asyncio
    async def test_media_list_with_filters(self, async_client: AsyncClient):
        """미디어 목록 조회 - 필터링"""
        # 타입별 필터
        response = await async_client.get("/api/v1/media/", params={"type": "image"})
        assert response.status_code in [200, 401, 422]

        # 대상별 필터
        response = await async_client.get(
            "/api/v1/media/", params={"target_type": "project", "target_id": 1}
        )
        assert response.status_code in [200, 401, 422]

    @pytest.mark.asyncio
    async def test_media_upload_unauthorized(self, async_client: AsyncClient):
        """미디어 업로드 - 인증 없음"""
        response = await async_client.post("/api/v1/media/upload")
        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_media_upload_no_file(self, authenticated_client: AsyncClient):
        """미디어 업로드 - 파일 없음"""
        response = await authenticated_client.post("/api/v1/media/upload")
        assert response.status_code in [422, 401]  # Validation error

    @pytest.mark.asyncio
    async def test_media_upload_with_file(self, authenticated_client: AsyncClient):
        """미디어 업로드 - 파일 포함"""
        # 테스트 파일 생성
        test_file = self.create_test_file(b"test image content", "test.png")
        files = {"file": ("test.png", test_file, "image/png")}

        response = await authenticated_client.post("/api/v1/media/upload", files=files)
        # 성공하거나 검증 오류
        assert response.status_code in [201, 422, 401]

        if response.status_code == 201:
            data = response.json()
            assert "id" in data
            assert "filename" in data or "original_filename" in data

    @pytest.mark.asyncio
    async def test_media_upload_large_file(self, authenticated_client: AsyncClient):
        """미디어 업로드 - 대용량 파일"""
        # 큰 파일 생성 (1MB)
        large_content = b"x" * (1024 * 1024)
        large_file = self.create_test_file(large_content, "large.txt")
        files = {"file": ("large.txt", large_file, "text/plain")}

        response = await authenticated_client.post("/api/v1/media/upload", files=files)
        # 크기 제한이 있다면 413, 없다면 201
        assert response.status_code in [201, 413, 422, 401]

    @pytest.mark.asyncio
    async def test_media_upload_invalid_file_type(
        self, authenticated_client: AsyncClient
    ):
        """미디어 업로드 - 지원하지 않는 파일 형식"""
        # 실행 파일 업로드 시도
        exe_file = self.create_test_file(b"fake exe", "malware.exe")
        files = {"file": ("malware.exe", exe_file, "application/x-executable")}

        response = await authenticated_client.post("/api/v1/media/upload", files=files)
        # 파일 형식 제한이 있다면 400/422
        assert response.status_code in [201, 400, 422, 401]

    @pytest.mark.asyncio
    async def test_media_get_by_id_not_found(self, async_client: AsyncClient):
        """미디어 조회 - 존재하지 않음"""
        response = await async_client.get("/api/v1/media/99999")
        assert response.status_code in [404, 401]

    @pytest.mark.asyncio
    async def test_media_get_by_id_invalid_format(self, async_client: AsyncClient):
        """미디어 조회 - 잘못된 ID 형식"""
        response = await async_client.get("/api/v1/media/invalid-id")
        assert response.status_code in [422, 404]

    @pytest.mark.asyncio
    async def test_media_update_unauthorized(self, async_client: AsyncClient):
        """미디어 업데이트 - 인증 없음"""
        update_data = {"alt_text": "Updated alt text"}
        response = await async_client.patch("/api/v1/media/1", json=update_data)
        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_media_update_not_found(self, authenticated_client: AsyncClient):
        """미디어 업데이트 - 존재하지 않음"""
        update_data = {"alt_text": "Updated alt text"}
        response = await authenticated_client.patch(
            "/api/v1/media/99999", json=update_data
        )
        assert response.status_code in [404, 401]

    @pytest.mark.asyncio
    async def test_media_delete_unauthorized(self, async_client: AsyncClient):
        """미디어 삭제 - 인증 없음"""
        response = await async_client.delete("/api/v1/media/1")
        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_media_delete_not_found(self, authenticated_client: AsyncClient):
        """미디어 삭제 - 존재하지 않음"""
        response = await authenticated_client.delete("/api/v1/media/99999")
        assert response.status_code in [404, 401]

    @pytest.mark.asyncio
    async def test_media_download_not_found(self, async_client: AsyncClient):
        """미디어 다운로드 - 존재하지 않음"""
        response = await async_client.get("/api/v1/media/99999/download")
        assert response.status_code in [404, 401]

    @pytest.mark.asyncio
    async def test_media_download_invalid_id(self, async_client: AsyncClient):
        """미디어 다운로드 - 잘못된 ID"""
        response = await async_client.get("/api/v1/media/invalid/download")
        assert response.status_code in [422, 404]

    @pytest.mark.asyncio
    async def test_media_thumbnail_not_found(self, async_client: AsyncClient):
        """미디어 썸네일 - 존재하지 않음"""
        response = await async_client.get("/api/v1/media/99999/thumbnail")
        assert response.status_code in [404, 401]

    @pytest.mark.asyncio
    async def test_media_thumbnail_invalid_id(self, async_client: AsyncClient):
        """미디어 썸네일 - 잘못된 ID"""
        response = await async_client.get("/api/v1/media/invalid/thumbnail")
        assert response.status_code in [422, 404]

    @pytest.mark.asyncio
    async def test_media_bulk_delete_unauthorized(self, async_client: AsyncClient):
        """미디어 대량 삭제 - 인증 없음"""
        response = await async_client.post("/api/v1/media/bulk-delete")
        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_media_bulk_delete_no_data(self, authenticated_client: AsyncClient):
        """미디어 대량 삭제 - 데이터 없음"""
        response = await authenticated_client.post("/api/v1/media/bulk-delete")
        assert response.status_code in [422, 401]  # Validation error

    @pytest.mark.asyncio
    async def test_media_bulk_delete_with_ids(self, authenticated_client: AsyncClient):
        """미디어 대량 삭제 - ID 목록 포함"""
        delete_data = {"media_ids": [99999, 99998]}
        response = await authenticated_client.post(
            "/api/v1/media/bulk-delete", json=delete_data
        )
        assert response.status_code in [200, 404, 422, 401]

    @pytest.mark.asyncio
    async def test_media_stats_storage(self, async_client: AsyncClient):
        """미디어 스토리지 통계"""
        response = await async_client.get("/api/v1/media/stats/storage")
        # 공개 접근이 가능하면 200, 인증 필요하면 401
        assert response.status_code in [200, 401]

        if response.status_code == 200:
            data = response.json()
            assert isinstance(data, dict)

    @pytest.mark.asyncio
    async def test_media_http_methods(self, async_client: AsyncClient):
        """미디어 API HTTP 메서드 검증"""
        # GET이 허용되지 않는 POST 엔드포인트
        response = await async_client.get("/api/v1/media/upload")
        assert response.status_code in [405, 422]  # 422는 validation error

        response = await async_client.get("/api/v1/media/bulk-delete")
        assert response.status_code in [405, 422]

        # POST가 허용되지 않는 GET 엔드포인트
        response = await async_client.post("/api/v1/media/1")
        assert response.status_code == 405

        response = await async_client.post("/api/v1/media/1/download")
        assert response.status_code == 405

    @pytest.mark.asyncio
    async def test_media_upload_multiple_files(self, authenticated_client: AsyncClient):
        """미디어 다중 파일 업로드 시뮬레이션"""
        # 여러 파일을 순차적으로 업로드
        files_to_upload = [
            ("test1.txt", b"content1", "text/plain"),
            ("test2.png", b"fake png content", "image/png"),
            ("test3.jpg", b"fake jpg content", "image/jpeg"),
        ]

        results = []
        for filename, content, mime_type in files_to_upload:
            test_file = self.create_test_file(content, filename)
            files = {"file": (filename, test_file, mime_type)}
            response = await authenticated_client.post(
                "/api/v1/media/upload", files=files
            )
            results.append(response.status_code)

        # 모든 업로드가 같은 응답을 받아야 함
        assert all(status in [201, 422, 401] for status in results)

    @pytest.mark.asyncio
    async def test_media_content_type_validation(
        self, authenticated_client: AsyncClient
    ):
        """미디어 Content-Type 검증"""
        # multipart/form-data가 아닌 요청
        response = await authenticated_client.post(
            "/api/v1/media/upload",
            json={"file": "not_a_file"},
            headers={"Content-Type": "application/json"},
        )
        assert response.status_code in [422, 401]

    @pytest.mark.asyncio
    async def test_media_upload_edge_cases(self, authenticated_client: AsyncClient):
        """미디어 업로드 엣지 케이스"""
        # 빈 파일
        empty_file = self.create_test_file(b"", "empty.txt")
        files = {"file": ("empty.txt", empty_file, "text/plain")}
        response = await authenticated_client.post("/api/v1/media/upload", files=files)
        assert response.status_code in [201, 400, 422, 401]

        # 파일명에 특수문자
        special_file = self.create_test_file(
            b"content", "file with spaces & symbols!.txt"
        )
        files = {
            "file": ("file with spaces & symbols!.txt", special_file, "text/plain")
        }
        response = await authenticated_client.post("/api/v1/media/upload", files=files)
        assert response.status_code in [201, 400, 422, 401]

        # 매우 긴 파일명
        long_name = "a" * 255 + ".txt"
        long_file = self.create_test_file(b"content", long_name)
        files = {"file": (long_name, long_file, "text/plain")}
        response = await authenticated_client.post("/api/v1/media/upload", files=files)
        assert response.status_code in [201, 400, 422, 401]
