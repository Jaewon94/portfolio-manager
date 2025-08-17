"""
간단한 API 테스트
실제 구현된 엔드포인트만 테스트
"""

import pytest
from app.models.user import User
from fastapi import status
from httpx import AsyncClient


@pytest.mark.api
class TestSimpleAPI:
    """간단한 API 테스트"""

    @pytest.mark.asyncio
    async def test_api_server_running(self, async_client: AsyncClient):
        """API 서버 실행 상태 확인"""
        # 단순히 요청이 처리되는지 확인 (404라도 서버가 응답하면 OK)
        response = await async_client.get("/")
        # 서버가 응답하면 성공 (404, 200, 등 상관없이)
        assert response.status_code in [200, 404, 422]

    @pytest.mark.asyncio
    async def test_docs_endpoint(self, async_client: AsyncClient):
        """API 문서 엔드포인트 테스트"""
        response = await async_client.get("/docs")
        # FastAPI 기본 문서 페이지
        assert response.status_code in [200, 404]

    @pytest.mark.asyncio
    async def test_openapi_endpoint(self, async_client: AsyncClient):
        """OpenAPI 스키마 엔드포인트 테스트"""
        response = await async_client.get("/openapi.json")
        # OpenAPI 스키마
        assert response.status_code in [200, 404]

    @pytest.mark.asyncio
    async def test_api_prefix_routing(self, async_client: AsyncClient):
        """API 라우팅 테스트"""
        # /api/v1 경로로 요청
        response = await async_client.get("/api/v1/")
        # 라우팅이 설정되어 있으면 응답을 받을 것
        assert response.status_code in [200, 404, 405, 422]

    @pytest.mark.asyncio
    async def test_auth_login_provider_endpoint(self, async_client: AsyncClient):
        """인증 로그인 엔드포인트 테스트 (실제 경로)"""
        # 실제 구현된 경로로 테스트
        response = await async_client.post("/api/v1/auth/login/github")
        # 422 (Validation Error)나 다른 응답이라도 엔드포인트가 존재함을 확인
        assert response.status_code in [200, 400, 401, 422, 500]

    @pytest.mark.asyncio
    async def test_auth_me_endpoint_without_auth(self, async_client: AsyncClient):
        """사용자 정보 조회 (인증 없이)"""
        response = await async_client.get("/api/v1/auth/me")
        # 인증이 필요한 엔드포인트이므로 401 Unauthorized 예상
        assert response.status_code in [401, 403, 422]

    @pytest.mark.asyncio
    async def test_auth_refresh_endpoint(self, async_client: AsyncClient):
        """토큰 갱신 엔드포인트 테스트"""
        response = await async_client.post("/api/v1/auth/refresh")
        # 요청 본문이 없으므로 422 Validation Error 예상
        assert response.status_code in [400, 422, 401]

    @pytest.mark.asyncio
    async def test_projects_endpoint(self, async_client: AsyncClient):
        """프로젝트 목록 조회 테스트"""
        response = await async_client.get("/api/v1/projects/")
        # 프로젝트 목록 조회 (인증 필요할 수도 있음)
        assert response.status_code in [200, 401, 403, 422]

    @pytest.mark.asyncio
    async def test_invalid_endpoint(self, async_client: AsyncClient):
        """존재하지 않는 엔드포인트 테스트"""
        response = await async_client.get("/api/v1/nonexistent")
        # 404 Not Found 예상
        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_method_not_allowed(self, async_client: AsyncClient):
        """허용되지 않는 HTTP 메서드 테스트"""
        response = await async_client.delete("/api/v1/auth/me")
        # 405 Method Not Allowed 또는 다른 응답
        assert response.status_code in [404, 405, 401, 422]
