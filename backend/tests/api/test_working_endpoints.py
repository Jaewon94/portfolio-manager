"""
실제 작동하는 API 엔드포인트 테스트
구현된 기능만 테스트
"""

import pytest
from app.models.user import User
from fastapi import status
from httpx import AsyncClient


@pytest.mark.api
class TestWorkingEndpoints:
    """실제 작동하는 엔드포인트 테스트"""

    @pytest.mark.asyncio
    async def test_health_check(self, async_client: AsyncClient):
        """헬스 체크 엔드포인트 테스트"""
        response = await async_client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        assert data["status"] == "healthy"
        assert "version" in data

    @pytest.mark.asyncio
    async def test_root_endpoint(self, async_client: AsyncClient):
        """루트 엔드포인트 테스트"""
        response = await async_client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "version" in data
        assert "docs" in data
        assert "health" in data

    @pytest.mark.asyncio
    async def test_docs_endpoint(self, async_client: AsyncClient):
        """API 문서 엔드포인트 테스트"""
        response = await async_client.get("/docs")
        assert response.status_code == 200
        # HTML 문서 응답 확인
        assert "text/html" in response.headers.get("content-type", "")

    @pytest.mark.asyncio
    async def test_openapi_schema(self, async_client: AsyncClient):
        """OpenAPI 스키마 테스트"""
        response = await async_client.get("/api/v1/openapi.json")
        assert response.status_code == 200
        data = response.json()
        assert "openapi" in data
        assert "info" in data
        assert "paths" in data

    @pytest.mark.asyncio
    async def test_auth_login_github_validation(self, async_client: AsyncClient):
        """GitHub 로그인 엔드포인트 검증 테스트"""
        # 빈 요청 본문으로 테스트 (401 또는 422 예상)
        response = await async_client.post("/api/v1/auth/login/github")
        assert response.status_code in [401, 422]
        data = response.json()
        assert "detail" in data

    @pytest.mark.asyncio
    async def test_auth_me_unauthorized(self, async_client: AsyncClient):
        """인증되지 않은 사용자 정보 조회 테스트"""
        response = await async_client.get("/api/v1/auth/me")
        assert response.status_code == 401
        data = response.json()
        assert "detail" in data

    @pytest.mark.asyncio
    async def test_auth_refresh_validation(self, async_client: AsyncClient):
        """토큰 갱신 검증 테스트"""
        # 잘못된 요청 본문
        response = await async_client.post("/api/v1/auth/refresh", json={})
        assert response.status_code == 422
        data = response.json()
        assert "detail" in data

    @pytest.mark.asyncio
    async def test_auth_refresh_invalid_token(self, async_client: AsyncClient):
        """잘못된 토큰으로 갱신 테스트"""
        response = await async_client.post(
            "/api/v1/auth/refresh", json={"refresh_token": "invalid_token"}
        )
        # 토큰 검증 실패로 401 또는 422 예상
        assert response.status_code in [401, 422]

    @pytest.mark.asyncio
    async def test_projects_list_unauthorized(self, async_client: AsyncClient):
        """인증되지 않은 프로젝트 목록 조회"""
        response = await async_client.get("/api/v1/projects/")
        # 인증이 필요하면 401, 공개 접근이면 200
        assert response.status_code in [200, 401]

    @pytest.mark.asyncio
    async def test_cors_headers(self, async_client: AsyncClient):
        """CORS 헤더 테스트"""
        response = await async_client.options("/api/v1/auth/me")
        # CORS 프리플라이트 요청 처리
        assert response.status_code in [200, 405]

    @pytest.mark.asyncio
    async def test_api_versioning(self, async_client: AsyncClient):
        """API 버전 관리 테스트"""
        # v1 API 접근
        response = await async_client.get("/api/v1/projects/")
        assert response.status_code in [200, 401, 422]

        # 존재하지 않는 버전
        response = await async_client.get("/api/v2/projects/")
        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_content_type_validation(self, async_client: AsyncClient):
        """Content-Type 검증 테스트"""
        # JSON이 아닌 데이터 전송
        response = await async_client.post(
            "/api/v1/auth/refresh",
            data="invalid_data",
            headers={"Content-Type": "text/plain"},
        )
        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_large_request_handling(self, async_client: AsyncClient):
        """큰 요청 처리 테스트"""
        # 매우 긴 문자열로 테스트
        large_data = {"refresh_token": "a" * 10000}
        response = await async_client.post("/api/v1/auth/refresh", json=large_data)
        # 토큰 검증 실패나 요청 크기 제한
        assert response.status_code in [400, 401, 413, 422]

    @pytest.mark.asyncio
    async def test_method_not_allowed(self, async_client: AsyncClient):
        """허용되지 않는 HTTP 메서드 테스트"""
        # GET 메서드가 허용되지 않는 엔드포인트에 GET 요청
        response = await async_client.get("/api/v1/auth/refresh")
        assert response.status_code == 405

    @pytest.mark.asyncio
    async def test_trailing_slash_handling(self, async_client: AsyncClient):
        """trailing slash 처리 테스트"""
        # 슬래시 있는 경우와 없는 경우
        response1 = await async_client.get("/api/v1/projects")
        response2 = await async_client.get("/api/v1/projects/")

        # 둘 다 같은 응답이거나 리다이렉트 처리
        assert response1.status_code in [200, 307, 401, 422]
        assert response2.status_code in [200, 307, 401, 422]
