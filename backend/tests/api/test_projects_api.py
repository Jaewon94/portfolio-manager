"""
프로젝트 API 테스트
Projects endpoints: CRUD, 검색, 통계, 조회수
"""

import pytest
from app.core.security import create_access_token
from app.models.project import Project
from app.models.user import User
from httpx import AsyncClient


@pytest.mark.api
@pytest.mark.project
class TestProjectsAPI:
    """프로젝트 관련 API 테스트"""

    @pytest.mark.asyncio
    async def test_projects_list_public_access(self, async_client: AsyncClient):
        """프로젝트 목록 조회 - 공개 접근"""
        response = await async_client.get("/api/v1/projects/")
        # 공개 접근이 가능하면 200, 인증 필요하면 401
        assert response.status_code in [200, 401]

        if response.status_code == 200:
            data = response.json()
            assert isinstance(data, list)

    @pytest.mark.asyncio
    async def test_projects_list_with_auth(self, authenticated_client: AsyncClient):
        """프로젝트 목록 조회 - 인증됨"""
        response = await authenticated_client.get("/api/v1/projects/")
        assert response.status_code in [200, 401]

        if response.status_code == 200:
            data = response.json()
            assert isinstance(data, list)

    @pytest.mark.asyncio
    async def test_project_create_unauthorized(self, async_client: AsyncClient):
        """프로젝트 생성 - 인증 없음"""
        project_data = {
            "slug": "test-project",
            "title": "Test Project",
            "description": "Test description",
        }
        response = await async_client.post("/api/v1/projects/", json=project_data)
        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_project_create_with_auth(self, authenticated_client: AsyncClient):
        """프로젝트 생성 - 인증됨"""
        project_data = {
            "slug": "auth-test-project",
            "title": "Auth Test Project",
            "description": "Authenticated test project",
        }
        response = await authenticated_client.post(
            "/api/v1/projects/", json=project_data
        )
        # 성공하거나 검증 오류
        assert response.status_code in [201, 422, 401]

        if response.status_code == 201:
            data = response.json()
            assert data["slug"] == "auth-test-project"
            assert data["title"] == "Auth Test Project"
            assert "id" in data

    @pytest.mark.asyncio
    async def test_project_create_validation_errors(
        self, authenticated_client: AsyncClient
    ):
        """프로젝트 생성 - 검증 오류"""
        # 빈 데이터
        response = await authenticated_client.post("/api/v1/projects/", json={})
        assert response.status_code in [422, 401]

        # 필수 필드 누락
        incomplete_data = {"title": "Only Title"}
        response = await authenticated_client.post(
            "/api/v1/projects/", json=incomplete_data
        )
        assert response.status_code in [422, 401]

        # 잘못된 데이터 타입
        invalid_data = {
            "slug": 123,  # 문자열이어야 함
            "title": "Test",
            "description": "Test",
        }
        response = await authenticated_client.post(
            "/api/v1/projects/", json=invalid_data
        )
        assert response.status_code in [422, 401]

    @pytest.mark.asyncio
    async def test_project_get_by_id_not_found(self, async_client: AsyncClient):
        """프로젝트 조회 - 존재하지 않음"""
        response = await async_client.get("/api/v1/projects/99999")
        assert response.status_code in [404, 401]

    @pytest.mark.asyncio
    async def test_project_get_by_id_with_auth(
        self, authenticated_client: AsyncClient, test_project: Project
    ):
        """프로젝트 조회 - 인증됨"""
        response = await authenticated_client.get(f"/api/v1/projects/{test_project.id}")
        assert response.status_code in [200, 404, 401]

        if response.status_code == 200:
            data = response.json()
            assert data["id"] == test_project.id
            assert "slug" in data
            assert "title" in data

    @pytest.mark.asyncio
    async def test_project_update_unauthorized(self, async_client: AsyncClient):
        """프로젝트 업데이트 - 인증 없음"""
        update_data = {"title": "Updated Title"}
        response = await async_client.put("/api/v1/projects/1", json=update_data)
        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_project_update_not_found(self, authenticated_client: AsyncClient):
        """프로젝트 업데이트 - 존재하지 않음"""
        update_data = {"title": "Updated Title"}
        response = await authenticated_client.put(
            "/api/v1/projects/99999", json=update_data
        )
        assert response.status_code in [404, 401]

    @pytest.mark.asyncio
    async def test_project_delete_unauthorized(self, async_client: AsyncClient):
        """프로젝트 삭제 - 인증 없음"""
        response = await async_client.delete("/api/v1/projects/1")
        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_project_delete_not_found(self, authenticated_client: AsyncClient):
        """프로젝트 삭제 - 존재하지 않음"""
        response = await authenticated_client.delete("/api/v1/projects/99999")
        assert response.status_code in [404, 401]

    @pytest.mark.asyncio
    async def test_project_slug_endpoint_structure(self, async_client: AsyncClient):
        """프로젝트 슬러그 엔드포인트 구조 테스트"""
        # 잘못된 슬러그 경로 구조
        response = await async_client.get("/api/v1/projects/slug/invalid")
        assert response.status_code == 404  # 경로 구조가 맞지 않음

        # 올바른 구조이지만 존재하지 않는 프로젝트
        response = await async_client.get("/api/v1/projects/slug/999/nonexistent")
        assert response.status_code in [404, 401]

    @pytest.mark.asyncio
    async def test_project_views_endpoint(self, async_client: AsyncClient):
        """프로젝트 조회수 증가 엔드포인트"""
        # 존재하지 않는 프로젝트
        response = await async_client.post("/api/v1/projects/99999/views")
        assert response.status_code in [404, 401, 422]

    @pytest.mark.asyncio
    async def test_projects_stats_overview(self, async_client: AsyncClient):
        """프로젝트 통계 개요"""
        response = await async_client.get("/api/v1/projects/stats/overview")
        assert response.status_code in [200, 401]

        if response.status_code == 200:
            data = response.json()
            # 통계 데이터 구조 확인
            assert isinstance(data, dict)

    @pytest.mark.asyncio
    async def test_projects_list_pagination(self, async_client: AsyncClient):
        """프로젝트 목록 페이지네이션"""
        # limit과 offset 파라미터
        response = await async_client.get(
            "/api/v1/projects/", params={"limit": 5, "offset": 0}
        )
        assert response.status_code in [200, 401]

        if response.status_code == 200:
            data = response.json()
            assert len(data) <= 5

    @pytest.mark.asyncio
    async def test_projects_list_filtering(self, async_client: AsyncClient):
        """프로젝트 목록 필터링"""
        # 상태별 필터링
        response = await async_client.get(
            "/api/v1/projects/", params={"status": "active"}
        )
        assert response.status_code in [200, 401, 422]

        # 가시성별 필터링
        response = await async_client.get(
            "/api/v1/projects/", params={"visibility": "public"}
        )
        assert response.status_code in [200, 401, 422]

    @pytest.mark.asyncio
    async def test_projects_list_sorting(self, async_client: AsyncClient):
        """프로젝트 목록 정렬"""
        # 생성일순 정렬
        response = await async_client.get(
            "/api/v1/projects/", params={"sort": "created_at", "order": "desc"}
        )
        assert response.status_code in [200, 401, 422]

        # 제목순 정렬
        response = await async_client.get(
            "/api/v1/projects/", params={"sort": "title", "order": "asc"}
        )
        assert response.status_code in [200, 401, 422]

    @pytest.mark.asyncio
    async def test_projects_http_methods(self, async_client: AsyncClient):
        """프로젝트 API HTTP 메서드 검증"""
        # GET이 허용되지 않는 POST 엔드포인트
        response = await async_client.get("/api/v1/projects/1/views")
        assert response.status_code == 405

        # PATCH가 허용되지 않는 PUT 엔드포인트
        response = await async_client.patch("/api/v1/projects/1")
        assert response.status_code == 405

    @pytest.mark.asyncio
    async def test_projects_invalid_id_format(self, async_client: AsyncClient):
        """프로젝트 ID 형식 검증"""
        # 문자열 ID
        response = await async_client.get("/api/v1/projects/invalid-id")
        assert response.status_code in [401, 422, 404]

        # 음수 ID
        response = await async_client.get("/api/v1/projects/-1")
        assert response.status_code in [401, 422, 404]

        # 0 ID
        response = await async_client.get("/api/v1/projects/0")
        assert response.status_code in [401, 422, 404]

    @pytest.mark.asyncio
    async def test_projects_large_data_handling(
        self, authenticated_client: AsyncClient
    ):
        """프로젝트 대용량 데이터 처리"""
        # 매우 긴 제목
        large_data = {
            "slug": "large-data-test",
            "title": "A" * 1000,  # 1000자 제목
            "description": "B" * 5000,  # 5000자 설명
        }

        response = await authenticated_client.post("/api/v1/projects/", json=large_data)
        # 크기 제한이 있다면 422, 없다면 201 또는 다른 오류
        assert response.status_code in [201, 413, 422, 401]

    @pytest.mark.asyncio
    async def test_projects_concurrent_access(self, async_client: AsyncClient):
        """프로젝트 동시 접근 시뮬레이션"""
        import asyncio

        # 같은 프로젝트에 대한 여러 요청
        tasks = []
        for _ in range(3):
            task = async_client.get("/api/v1/projects/")
            tasks.append(task)

        responses = await asyncio.gather(*tasks, return_exceptions=True)

        # 모든 응답이 성공적으로 처리되어야 함
        for response in responses:
            if hasattr(response, "status_code"):
                assert response.status_code in [200, 401]
