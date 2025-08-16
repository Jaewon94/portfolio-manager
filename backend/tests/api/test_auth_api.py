"""
인증 API 테스트
OAuth 로그인, JWT 토큰 발급/갱신, 로그아웃 테스트
"""

import pytest
from datetime import datetime, timezone
from httpx import AsyncClient
from unittest.mock import AsyncMock, patch
import json

from app.main import app
from app.core.config import settings
from app.core.security import create_access_token, create_refresh_token
from app.models.user import User, UserRole
from app.schemas.auth import OAuthUserInfo


class TestAuthAPI:
    """인증 API 테스트 클래스"""
    
    @pytest.mark.asyncio
    async def test_health_check(self):
        """기본 health check 테스트"""
        async with AsyncClient(app=app, base_url="http://test") as client:
            response = await client.get("/health")
            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "healthy"
            assert "version" in data
    
    @pytest.mark.asyncio
    async def test_oauth_login_invalid_provider(self):
        """지원되지 않는 OAuth 제공자 테스트"""
        async with AsyncClient(app=app, base_url="http://test") as client:
            response = await client.post(
                "/api/v1/auth/login/invalid",
                headers={"Authorization": "Bearer test-code"}
            )
            assert response.status_code == 400
            assert "Unsupported OAuth provider" in response.json()["detail"]
    
    @pytest.mark.asyncio
    async def test_oauth_login_missing_auth_header(self):
        """Authorization 헤더 누락 테스트"""
        async with AsyncClient(app=app, base_url="http://test") as client:
            response = await client.post("/api/v1/auth/login/github")
            assert response.status_code == 401
            assert "OAuth authorization code required" in response.json()["detail"]
    
    @pytest.mark.asyncio
    @patch('app.services.auth.AuthService.get_oauth_user_info')
    @patch('app.services.auth.AuthService.create_or_update_oauth_user')
    @patch('app.services.auth.AuthService.create_user_session')
    async def test_github_oauth_login_success(
        self, 
        mock_create_session,
        mock_create_user,
        mock_get_user_info
    ):
        """GitHub OAuth 로그인 성공 테스트"""
        # Mock 사용자 정보
        mock_oauth_user = OAuthUserInfo(
            provider_user_id="12345",
            email="test@github.com",
            name="Test User",
            avatar_url="https://avatars.githubusercontent.com/u/12345",
            github_username="testuser"
        )
        
        mock_user = User(
            id="user-uuid",
            email="test@github.com",
            name="Test User",
            github_username="testuser",
            role=UserRole.USER,
            is_verified=True,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc)
        )
        
        # Mock 설정
        mock_get_user_info.return_value = mock_oauth_user
        mock_create_user.return_value = mock_user
        mock_create_session.return_value = AsyncMock()
        
        async with AsyncClient(app=app, base_url="http://test") as client:
            response = await client.post(
                "/api/v1/auth/login/github",
                headers={"Authorization": "Bearer test-oauth-code"}
            )
            
            assert response.status_code == 200
            data = response.json()
            
            # 토큰 응답 검증
            assert "access_token" in data
            assert "refresh_token" in data
            assert data["token_type"] == "bearer"
            assert data["expires_in"] == settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
            
            # 사용자 정보 검증
            user_data = data["user"]
            assert user_data["id"] == "user-uuid"
            assert user_data["email"] == "test@github.com"
            assert user_data["name"] == "Test User"
            assert user_data["github_username"] == "testuser"
            assert user_data["role"] == UserRole.USER.value
            assert user_data["is_verified"] is True
            
            # Mock 호출 검증
            mock_get_user_info.assert_called_once_with("github", "test-oauth-code")
            mock_create_user.assert_called_once_with("github", mock_oauth_user)
            mock_create_session.assert_called_once()
    
    @pytest.mark.asyncio
    @patch('app.services.auth.AuthService.get_oauth_user_info')
    async def test_oauth_login_user_info_failure(self, mock_get_user_info):
        """OAuth 사용자 정보 조회 실패 테스트"""
        mock_get_user_info.side_effect = Exception("OAuth API failed")
        
        async with AsyncClient(app=app, base_url="http://test") as client:
            response = await client.post(
                "/api/v1/auth/login/google",
                headers={"Authorization": "Bearer invalid-code"}
            )
            
            assert response.status_code == 400
            assert "OAuth login failed" in response.json()["detail"]
    
    @pytest.mark.asyncio
    async def test_refresh_token_invalid(self):
        """유효하지 않은 refresh token 테스트"""
        async with AsyncClient(app=app, base_url="http://test") as client:
            response = await client.post(
                "/api/v1/auth/refresh",
                json={"refresh_token": "invalid-token"}
            )
            
            assert response.status_code == 401
            assert "Could not validate credentials" in response.json()["detail"]
    
    @pytest.mark.asyncio
    @patch('app.services.auth.AuthService.get_user_by_id')
    async def test_refresh_token_success(self, mock_get_user):
        """Refresh token 성공 테스트"""
        mock_user = User(
            id="user-uuid",
            email="test@example.com",
            name="Test User",
            role=UserRole.USER,
            is_verified=True,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc)
        )
        mock_get_user.return_value = mock_user
        
        # 유효한 refresh token 생성
        refresh_token = create_refresh_token(subject="user-uuid")
        
        async with AsyncClient(app=app, base_url="http://test") as client:
            response = await client.post(
                "/api/v1/auth/refresh",
                json={"refresh_token": refresh_token}
            )
            
            assert response.status_code == 200
            data = response.json()
            
            assert "access_token" in data
            assert data["refresh_token"] == refresh_token  # 기존 refresh token 유지
            assert data["token_type"] == "bearer"
            assert data["expires_in"] == settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
    
    @pytest.mark.asyncio
    async def test_get_current_user_unauthorized(self):
        """인증되지 않은 사용자 정보 조회 테스트"""
        async with AsyncClient(app=app, base_url="http://test") as client:
            response = await client.get("/api/v1/auth/me")
            
            assert response.status_code == 401
            assert "Authorization token required" in response.json()["detail"]
    
    @pytest.mark.asyncio
    @patch('app.services.auth.AuthService.get_user_by_id')
    async def test_get_current_user_success(self, mock_get_user):
        """인증된 사용자 정보 조회 성공 테스트"""
        mock_user = User(
            id="user-uuid",
            email="test@example.com",
            name="Test User",
            role=UserRole.USER,
            is_verified=True,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc)
        )
        mock_get_user.return_value = mock_user
        
        # 유효한 access token 생성
        access_token = create_access_token(subject="user-uuid")
        
        async with AsyncClient(app=app, base_url="http://test") as client:
            response = await client.get(
                "/api/v1/auth/me",
                headers={"Authorization": f"Bearer {access_token}"}
            )
            
            assert response.status_code == 200
            data = response.json()
            
            assert data["id"] == "user-uuid"
            assert data["email"] == "test@example.com"
            assert data["name"] == "Test User"
            assert data["role"] == UserRole.USER.value
            assert data["is_verified"] is True
    
    @pytest.mark.asyncio
    @patch('app.services.auth.AuthService.invalidate_user_sessions')
    @patch('app.services.auth.AuthService.get_user_by_id')
    async def test_logout_success(self, mock_get_user, mock_invalidate_sessions):
        """로그아웃 성공 테스트"""
        mock_user = User(
            id="user-uuid",
            email="test@example.com",
            name="Test User",
            role=UserRole.USER,
            is_verified=True,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc)
        )
        mock_get_user.return_value = mock_user
        mock_invalidate_sessions.return_value = None
        
        # 유효한 access token 생성
        access_token = create_access_token(subject="user-uuid")
        
        async with AsyncClient(app=app, base_url="http://test") as client:
            response = await client.post(
                "/api/v1/auth/logout",
                headers={"Authorization": f"Bearer {access_token}"}
            )
            
            assert response.status_code == 200
            assert response.json()["message"] == "Successfully logged out"
            
            # 세션 무효화 호출 검증
            mock_invalidate_sessions.assert_called_once_with("user-uuid")
    
    @pytest.mark.asyncio
    async def test_test_login_production_disabled(self):
        """프로덕션 환경에서 테스트 로그인 비활성화 테스트"""
        with patch.object(settings, 'ENVIRONMENT', 'production'):
            async with AsyncClient(app=app, base_url="http://test") as client:
                response = await client.post(
                    "/api/v1/auth/test-login",
                    json={"email": "test@example.com", "password": "testpass"}
                )
                
                assert response.status_code == 404
                assert "Test login not available in production" in response.json()["detail"]
    
    @pytest.mark.asyncio
    @patch('app.services.auth.AuthService.create_test_user')
    @patch('app.services.auth.AuthService.get_user_by_email')
    async def test_test_login_create_new_user(self, mock_get_user, mock_create_user):
        """테스트 로그인 - 새 사용자 생성 테스트"""
        mock_get_user.return_value = None  # 기존 사용자 없음
        
        mock_new_user = User(
            id="new-user-uuid",
            email="newuser@example.com",
            name="newuser",
            role=UserRole.USER,
            is_verified=True,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc)
        )
        mock_create_user.return_value = mock_new_user
        
        async with AsyncClient(app=app, base_url="http://test") as client:
            response = await client.post(
                "/api/v1/auth/test-login",
                json={"email": "newuser@example.com", "password": "testpass123"}
            )
            
            assert response.status_code == 200
            data = response.json()
            
            assert "access_token" in data
            assert "refresh_token" in data
            assert data["user"]["email"] == "newuser@example.com"
            assert data["user"]["name"] == "newuser"
            
            # Mock 호출 검증
            mock_create_user.assert_called_once_with(
                email="newuser@example.com", 
                name="newuser", 
                password="testpass123"
            )


class TestOAuthProviders:
    """개별 OAuth 제공자 테스트"""
    
    @pytest.mark.asyncio
    @patch('httpx.AsyncClient')
    async def test_github_oauth_token_exchange_failure(self, mock_client):
        """GitHub OAuth 토큰 교환 실패 테스트"""
        # Mock HTTP 클라이언트 설정
        mock_response = AsyncMock()
        mock_response.status_code = 400
        mock_response.text = "Invalid client"
        mock_response.json.return_value = {"error": "invalid_client"}
        
        mock_client_instance = AsyncMock()
        mock_client_instance.post.return_value = mock_response
        mock_client.return_value.__aenter__.return_value = mock_client_instance
        
        from app.services.auth import AuthService
        
        # 가짜 DB 세션
        mock_db = AsyncMock()
        auth_service = AuthService(mock_db)
        
        with pytest.raises(Exception) as exc_info:
            await auth_service._get_github_user_info("invalid-code")
        
        assert "GitHub OAuth token exchange failed" in str(exc_info.value)
    
    @pytest.mark.asyncio
    @patch('httpx.AsyncClient')
    async def test_google_oauth_people_api_fallback(self, mock_client):
        """Google OAuth People API 실패 시 userinfo v2 폴백 테스트"""
        # Mock HTTP 클라이언트 설정
        mock_token_response = AsyncMock()
        mock_token_response.status_code = 200
        mock_token_response.json.return_value = {"access_token": "test-token"}
        
        # People API 실패, userinfo v2 성공
        mock_people_response = AsyncMock()
        mock_people_response.status_code = 403  # People API 접근 실패
        
        mock_userinfo_response = AsyncMock()
        mock_userinfo_response.status_code = 200
        mock_userinfo_response.json = AsyncMock(return_value={
            "id": "google123",
            "email": "test@gmail.com",
            "name": "Test User",
            "picture": "https://lh3.googleusercontent.com/test"
        })
        
        mock_client_instance = AsyncMock()
        mock_client_instance.post.return_value = mock_token_response
        mock_client_instance.get.side_effect = [mock_people_response, mock_userinfo_response]
        mock_client.return_value.__aenter__.return_value = mock_client_instance
        
        from app.services.auth import AuthService
        
        # 가짜 DB 세션
        mock_db = AsyncMock()
        auth_service = AuthService(mock_db)
        
        result = await auth_service._get_google_user_info("test-code")
        
        assert result.provider_user_id == "google123"
        assert result.email == "test@gmail.com"
        assert result.name == "Test User"
        assert result.avatar_url == "https://lh3.googleusercontent.com/test"
    
    @pytest.mark.asyncio
    @patch('httpx.AsyncClient')
    async def test_kakao_oauth_no_email_consent(self, mock_client):
        """카카오 OAuth 이메일 동의 없음 테스트"""
        # Mock HTTP 클라이언트 설정
        mock_token_response = AsyncMock()
        mock_token_response.status_code = 200
        mock_token_response.json = AsyncMock(return_value={"access_token": "test-token"})
        
        mock_user_response = AsyncMock()
        mock_user_response.status_code = 200
        mock_user_response.json = AsyncMock(return_value={
            "id": 123456789,
            "kakao_account": {
                "profile": {
                    "nickname": "테스트유저",
                    "profile_image_url": "https://k.kakaocdn.net/test.jpg"
                }
                # 이메일 정보 없음 (동의 안함)
            }
        })
        
        mock_client_instance = AsyncMock()
        mock_client_instance.post.return_value = mock_token_response
        mock_client_instance.get.return_value = mock_user_response
        mock_client.return_value.__aenter__.return_value = mock_client_instance
        
        from app.services.auth import AuthService
        
        # 가짜 DB 세션
        mock_db = AsyncMock()
        auth_service = AuthService(mock_db)
        
        result = await auth_service._get_kakao_user_info("test-code")
        
        assert result.provider_user_id == "123456789"
        assert result.email == "kakao_123456789@kakao.local"  # 임시 이메일
        assert result.name == "테스트유저"
        assert result.avatar_url == "https://k.kakaocdn.net/test.jpg"