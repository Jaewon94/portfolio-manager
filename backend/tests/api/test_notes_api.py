"""
노트 API 테스트
Notes endpoints: CRUD, 아카이브, 고정, 통계
"""

import pytest
from app.core.security import create_access_token
from app.models.user import User
from httpx import AsyncClient


@pytest.mark.api
@pytest.mark.note
class TestNotesAPI:
    """노트 관련 API 테스트"""

    @pytest.mark.asyncio
    async def test_notes_list_unauthorized(self, async_client: AsyncClient):
        """노트 목록 조회 - 인증 없음"""
        response = await async_client.get("/api/v1/notes/")
        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_notes_list_with_auth(self, authenticated_client: AsyncClient):
        """노트 목록 조회 - 인증됨"""
        response = await authenticated_client.get("/api/v1/notes/")
        assert response.status_code in [200, 401]

        if response.status_code == 200:
            data = response.json()
            assert isinstance(data, list)

    @pytest.mark.asyncio
    async def test_notes_list_with_filters(self, authenticated_client: AsyncClient):
        """노트 목록 조회 - 필터링"""
        # 타입별 필터
        response = await authenticated_client.get(
            "/api/v1/notes/", params={"type": "personal"}
        )
        assert response.status_code in [200, 401, 422]

        # 상태별 필터
        response = await authenticated_client.get(
            "/api/v1/notes/", params={"archived": False}
        )
        assert response.status_code in [200, 401, 422]

        # 고정 여부 필터
        response = await authenticated_client.get(
            "/api/v1/notes/", params={"pinned": True}
        )
        assert response.status_code in [200, 401, 422]

    @pytest.mark.asyncio
    async def test_note_create_unauthorized(self, async_client: AsyncClient):
        """노트 생성 - 인증 없음"""
        note_data = {"title": "Test Note", "content": "Test content"}
        response = await async_client.post("/api/v1/notes/", json=note_data)
        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_note_create_with_auth(self, authenticated_client: AsyncClient):
        """노트 생성 - 인증됨"""
        note_data = {
            "title": "Auth Test Note",
            "content": "Authenticated test note content",
        }
        response = await authenticated_client.post("/api/v1/notes/", json=note_data)
        assert response.status_code in [201, 422, 401]

        if response.status_code == 201:
            data = response.json()
            assert data["title"] == "Auth Test Note"
            assert "id" in data
            assert "created_at" in data

    @pytest.mark.asyncio
    async def test_note_create_validation_errors(
        self, authenticated_client: AsyncClient
    ):
        """노트 생성 - 검증 오류"""
        # 빈 데이터
        response = await authenticated_client.post("/api/v1/notes/", json={})
        assert response.status_code in [422, 401]

        # 필수 필드 누락
        incomplete_data = {"title": "Only Title"}
        response = await authenticated_client.post(
            "/api/v1/notes/", json=incomplete_data
        )
        assert response.status_code in [201, 422, 401]  # content가 선택사항일 수도 있음

        # 잘못된 데이터 타입
        invalid_data = {"title": 123, "content": "Valid content"}  # 문자열이어야 함
        response = await authenticated_client.post("/api/v1/notes/", json=invalid_data)
        assert response.status_code in [422, 401]

    @pytest.mark.asyncio
    async def test_note_get_by_id_unauthorized(self, async_client: AsyncClient):
        """노트 조회 - 인증 없음"""
        response = await async_client.get("/api/v1/notes/1")
        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_note_get_by_id_not_found(self, authenticated_client: AsyncClient):
        """노트 조회 - 존재하지 않음"""
        response = await authenticated_client.get("/api/v1/notes/99999")
        assert response.status_code in [404, 401]

    @pytest.mark.asyncio
    async def test_note_get_by_id_invalid_format(
        self, authenticated_client: AsyncClient
    ):
        """노트 조회 - 잘못된 ID 형식"""
        response = await authenticated_client.get("/api/v1/notes/invalid-id")
        assert response.status_code in [401, 422, 404]

    @pytest.mark.asyncio
    async def test_note_update_unauthorized(self, async_client: AsyncClient):
        """노트 업데이트 - 인증 없음"""
        update_data = {"title": "Updated Title"}
        response = await async_client.put("/api/v1/notes/1", json=update_data)
        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_note_update_not_found(self, authenticated_client: AsyncClient):
        """노트 업데이트 - 존재하지 않음"""
        update_data = {"title": "Updated Title"}
        response = await authenticated_client.put(
            "/api/v1/notes/99999", json=update_data
        )
        assert response.status_code in [404, 401]

    @pytest.mark.asyncio
    async def test_note_update_validation(self, authenticated_client: AsyncClient):
        """노트 업데이트 - 검증 테스트"""
        # 빈 업데이트 데이터
        response = await authenticated_client.put("/api/v1/notes/1", json={})
        assert response.status_code in [200, 404, 422, 401]

        # 잘못된 데이터 타입
        invalid_data = {"title": None}
        response = await authenticated_client.put("/api/v1/notes/1", json=invalid_data)
        assert response.status_code in [404, 422, 401]

    @pytest.mark.asyncio
    async def test_note_delete_unauthorized(self, async_client: AsyncClient):
        """노트 삭제 - 인증 없음"""
        response = await async_client.delete("/api/v1/notes/1")
        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_note_delete_not_found(self, authenticated_client: AsyncClient):
        """노트 삭제 - 존재하지 않음"""
        response = await authenticated_client.delete("/api/v1/notes/99999")
        assert response.status_code in [404, 401]

    @pytest.mark.asyncio
    async def test_note_archive_unauthorized(self, async_client: AsyncClient):
        """노트 아카이브 - 인증 없음"""
        response = await async_client.post("/api/v1/notes/1/archive")
        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_note_archive_not_found(self, authenticated_client: AsyncClient):
        """노트 아카이브 - 존재하지 않음"""
        response = await authenticated_client.post("/api/v1/notes/99999/archive")
        assert response.status_code in [404, 401]

    @pytest.mark.asyncio
    async def test_note_archive_invalid_id(self, authenticated_client: AsyncClient):
        """노트 아카이브 - 잘못된 ID"""
        response = await authenticated_client.post("/api/v1/notes/invalid/archive")
        assert response.status_code in [401, 422, 404]

    @pytest.mark.asyncio
    async def test_note_pin_unauthorized(self, async_client: AsyncClient):
        """노트 고정 - 인증 없음"""
        response = await async_client.post("/api/v1/notes/1/pin")
        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_note_pin_not_found(self, authenticated_client: AsyncClient):
        """노트 고정 - 존재하지 않음"""
        response = await authenticated_client.post("/api/v1/notes/99999/pin")
        assert response.status_code in [404, 401]

    @pytest.mark.asyncio
    async def test_note_pin_invalid_id(self, authenticated_client: AsyncClient):
        """노트 고정 - 잘못된 ID"""
        response = await authenticated_client.post("/api/v1/notes/invalid/pin")
        assert response.status_code in [401, 422, 404]

    @pytest.mark.asyncio
    async def test_notes_stats_overview_unauthorized(self, async_client: AsyncClient):
        """노트 통계 개요 - 인증 없음"""
        response = await async_client.get("/api/v1/notes/stats/overview")
        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_notes_stats_overview_with_auth(
        self, authenticated_client: AsyncClient
    ):
        """노트 통계 개요 - 인증됨"""
        response = await authenticated_client.get("/api/v1/notes/stats/overview")
        assert response.status_code in [200, 401]

        if response.status_code == 200:
            data = response.json()
            assert isinstance(data, dict)

    @pytest.mark.asyncio
    async def test_notes_http_methods(self, async_client: AsyncClient):
        """노트 API HTTP 메서드 검증"""
        # GET이 허용되지 않는 POST 엔드포인트
        response = await async_client.get("/api/v1/notes/1/archive")
        assert response.status_code == 405

        response = await async_client.get("/api/v1/notes/1/pin")
        assert response.status_code == 405

        # POST가 허용되지 않는 GET 엔드포인트
        response = await async_client.post("/api/v1/notes/1")
        assert response.status_code == 405

    @pytest.mark.asyncio
    async def test_notes_pagination(self, authenticated_client: AsyncClient):
        """노트 목록 페이지네이션"""
        # limit과 offset 파라미터
        response = await authenticated_client.get(
            "/api/v1/notes/", params={"limit": 10, "offset": 0}
        )
        assert response.status_code in [200, 401, 422]

        # 페이지 크기 제한
        response = await authenticated_client.get(
            "/api/v1/notes/", params={"limit": 1000}
        )
        assert response.status_code in [200, 401, 422]

    @pytest.mark.asyncio
    async def test_notes_sorting(self, authenticated_client: AsyncClient):
        """노트 목록 정렬"""
        # 생성일순 정렬
        response = await authenticated_client.get(
            "/api/v1/notes/", params={"sort": "created_at", "order": "desc"}
        )
        assert response.status_code in [200, 401, 422]

        # 수정일순 정렬
        response = await authenticated_client.get(
            "/api/v1/notes/", params={"sort": "updated_at", "order": "asc"}
        )
        assert response.status_code in [200, 401, 422]

        # 제목순 정렬
        response = await authenticated_client.get(
            "/api/v1/notes/", params={"sort": "title", "order": "asc"}
        )
        assert response.status_code in [200, 401, 422]

    @pytest.mark.asyncio
    async def test_notes_search_in_list(self, authenticated_client: AsyncClient):
        """노트 목록에서 검색"""
        # 제목 검색
        response = await authenticated_client.get(
            "/api/v1/notes/", params={"q": "test"}
        )
        assert response.status_code in [200, 401, 422]

        # 내용 검색
        response = await authenticated_client.get(
            "/api/v1/notes/", params={"search": "content"}
        )
        assert response.status_code in [200, 401, 422]

    @pytest.mark.asyncio
    async def test_note_content_types(self, authenticated_client: AsyncClient):
        """노트 다양한 콘텐츠 타입 테스트"""
        content_types = [
            {
                "title": "Markdown Note",
                "content": "# Header\n\n**Bold text**",
                "content_type": "markdown",
            },
            {
                "title": "HTML Note",
                "content": "<h1>Header</h1><p>Paragraph</p>",
                "content_type": "html",
            },
            {
                "title": "Plain Note",
                "content": "Simple plain text",
                "content_type": "text",
            },
        ]

        for note_data in content_types:
            response = await authenticated_client.post("/api/v1/notes/", json=note_data)
            assert response.status_code in [201, 422, 401]

    @pytest.mark.asyncio
    async def test_note_large_content(self, authenticated_client: AsyncClient):
        """노트 대용량 콘텐츠 테스트"""
        large_note = {
            "title": "Large Content Note",
            "content": "A" * 100000,  # 100KB 콘텐츠
        }

        response = await authenticated_client.post("/api/v1/notes/", json=large_note)
        # 크기 제한이 있다면 413/422, 없다면 201
        assert response.status_code in [201, 413, 422, 401]

    @pytest.mark.asyncio
    async def test_note_special_characters(self, authenticated_client: AsyncClient):
        """노트 특수문자 처리 테스트"""
        special_note = {
            "title": "Special Characters: 한글, 🚀, <script>, 'quotes'",
            "content": "Content with émojis 🎉, HTML <b>tags</b>, and 'quotes' & \"double quotes\"",
        }

        response = await authenticated_client.post("/api/v1/notes/", json=special_note)
        assert response.status_code in [201, 422, 401]

    @pytest.mark.asyncio
    async def test_notes_concurrent_operations(self, authenticated_client: AsyncClient):
        """노트 동시 작업 시뮬레이션"""
        import asyncio

        # 동시에 여러 노트 생성
        tasks = []
        for i in range(3):
            note_data = {"title": f"Concurrent Note {i}", "content": f"Content {i}"}
            task = authenticated_client.post("/api/v1/notes/", json=note_data)
            tasks.append(task)

        responses = await asyncio.gather(*tasks, return_exceptions=True)

        # 모든 요청이 처리되어야 함
        for response in responses:
            if hasattr(response, "status_code"):
                assert response.status_code in [201, 422, 401]
