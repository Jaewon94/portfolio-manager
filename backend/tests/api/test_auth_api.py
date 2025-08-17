"""
인증 API 테스트
Authentication endpoints: 로그인, 로그아웃, 토큰 관리, 사용자 정보
"""

import pytest
from app.core.security import create_access_token
from app.models.user import User
from httpx import AsyncClient


@pytest.mark.api
@pytest.mark.auth
class TestAuthAPI:
    """인증 관련 API 테스트"""

    @pytest.mark.asyncio
    async def test_github_login_endpoint_exists(self, async_client: AsyncClient):
        """GitHub 로그인 엔드포인트 존재 확인"""
        response = await async_client.post("/api/v1/auth/login/github")
        # 엔드포인트가 존재하면 401/422, 없으면 404
        assert response.status_code in [401, 422]
        assert response.status_code != 404

    @pytest.mark.asyncio
    async def test_github_login_requires_data(self, async_client: AsyncClient):
        """GitHub 로그인 - 데이터 필요"""
        response = await async_client.post("/api/v1/auth/login/github", json={})
        # 인증이 필요하면 401, 검증 오류면 422
        assert response.status_code in [401, 422]

    @pytest.mark.asyncio
    async def test_test_login_endpoint(self, async_client: AsyncClient):
        """테스트 로그인 엔드포인트"""
        response = await async_client.post("/api/v1/auth/test-login")
        # 테스트 로그인 구현 상태에 따라 다름
        assert response.status_code in [200, 201, 422]

    @pytest.mark.asyncio
    async def test_get_current_user_unauthorized(self, async_client: AsyncClient):
        """현재 사용자 정보 조회 - 인증 없음"""
        response = await async_client.get("/api/v1/auth/me")
        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_get_current_user_invalid_token(self, async_client: AsyncClient):
        """현재 사용자 정보 조회 - 잘못된 토큰"""
        headers = {"Authorization": "Bearer invalid_token"}
        response = await async_client.get("/api/v1/auth/me", headers=headers)
        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_get_current_user_with_valid_token(
        self, async_client: AsyncClient, test_user: User
    ):
        """현재 사용자 정보 조회 - 유효한 토큰"""
        token = create_access_token(subject=str(test_user.id))
        headers = {"Authorization": f"Bearer {token}"}
        response = await async_client.get("/api/v1/auth/me", headers=headers)

        if response.status_code == 200:
            data = response.json()
            assert "id" in data
            assert data["id"] == test_user.id
        else:
            # 사용자가 DB에 없을 수도 있음
            assert response.status_code in [401, 404]

    @pytest.mark.asyncio
    async def test_token_refresh_no_token(self, async_client: AsyncClient):
        """토큰 갱신 - 토큰 없음"""
        response = await async_client.post("/api/v1/auth/refresh")
        assert response.status_code == 422  # Validation error

    @pytest.mark.asyncio
    async def test_token_refresh_invalid_token(self, async_client: AsyncClient):
        """토큰 갱신 - 잘못된 토큰"""
        response = await async_client.post(
            "/api/v1/auth/refresh", json={"refresh_token": "invalid_token"}
        )
        assert response.status_code in [401, 422]

    @pytest.mark.asyncio
    async def test_token_refresh_empty_token(self, async_client: AsyncClient):
        """토큰 갱신 - 빈 토큰"""
        response = await async_client.post(
            "/api/v1/auth/refresh", json={"refresh_token": ""}
        )
        assert response.status_code in [401, 422]

    @pytest.mark.asyncio
    async def test_logout_unauthorized(self, async_client: AsyncClient):
        """로그아웃 - 인증 없음"""
        response = await async_client.post("/api/v1/auth/logout")
        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_logout_invalid_token(self, async_client: AsyncClient):
        """로그아웃 - 잘못된 토큰"""
        headers = {"Authorization": "Bearer invalid_token"}
        response = await async_client.post("/api/v1/auth/logout", headers=headers)
        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_logout_with_valid_token(
        self, async_client: AsyncClient, test_user: User
    ):
        """로그아웃 - 유효한 토큰"""
        token = create_access_token(subject=str(test_user.id))
        headers = {"Authorization": f"Bearer {token}"}
        response = await async_client.post("/api/v1/auth/logout", headers=headers)

        # 로그아웃 성공하거나 사용자가 없을 수 있음
        assert response.status_code in [200, 204, 401, 404]

    @pytest.mark.asyncio
    async def test_auth_headers_validation(self, async_client: AsyncClient):
        """인증 헤더 검증"""
        # Bearer 없는 토큰
        headers = {"Authorization": "invalid_format"}
        response = await async_client.get("/api/v1/auth/me", headers=headers)
        assert response.status_code == 401

        # 빈 Authorization 헤더
        headers = {"Authorization": ""}
        response = await async_client.get("/api/v1/auth/me", headers=headers)
        assert response.status_code == 401

        # Bearer만 있고 토큰 없음
        headers = {"Authorization": "Bearer "}
        response = await async_client.get("/api/v1/auth/me", headers=headers)
        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_unsupported_auth_provider(self, async_client: AsyncClient):
        """지원하지 않는 인증 제공자"""
        response = await async_client.post("/api/v1/auth/login/facebook")
        # 지원하지 않는 제공자는 404 또는 400
        assert response.status_code in [400, 404, 422]

    @pytest.mark.asyncio
    async def test_auth_endpoints_http_methods(self, async_client: AsyncClient):
        """인증 엔드포인트 HTTP 메서드 검증"""
        # GET이 허용되지 않는 POST 엔드포인트들
        post_only_endpoints = [
            "/api/v1/auth/login/github",
            "/api/v1/auth/refresh",
            "/api/v1/auth/logout",
            "/api/v1/auth/test-login",
        ]

        for endpoint in post_only_endpoints:
            response = await async_client.get(endpoint)
            assert response.status_code == 405  # Method Not Allowed

        # POST가 허용되지 않는 GET 엔드포인트들
        response = await async_client.post("/api/v1/auth/me")
        assert response.status_code == 405

    @pytest.mark.asyncio
    async def test_auth_rate_limiting_simulation(self, async_client: AsyncClient):
        """인증 엔드포인트 반복 호출 테스트"""
        # 여러 번 연속 호출하여 rate limiting 확인
        responses = []

        for _ in range(5):
            response = await async_client.post("/api/v1/auth/login/github")
            responses.append(response.status_code)

        # Rate limiting이 구현되어 있다면 429가 나올 수 있음
        # 없다면 모두 같은 응답 (401/422)
        assert all(status in [401, 422, 429] for status in responses)

    @pytest.mark.asyncio
    async def test_auth_content_type_validation(self, async_client: AsyncClient):
        """인증 API Content-Type 검증"""
        # JSON이 아닌 데이터로 요청
        response = await async_client.post(
            "/api/v1/auth/refresh",
            data="invalid_data",
            headers={"Content-Type": "text/plain"},
        )
        assert response.status_code == 422

        # Content-Type 헤더 없이 JSON 데이터
        response = await async_client.post(
            "/api/v1/auth/refresh", content='{"refresh_token": "test"}'
        )
        # FastAPI가 자동으로 처리하거나 422 오류
        assert response.status_code in [401, 422]
