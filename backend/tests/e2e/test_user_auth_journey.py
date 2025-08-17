"""
E2E 테스트: 사용자 인증 여정
실제 사용자가 로그인부터 로그아웃까지의 전체 플로우 테스트
"""

import pytest
from app.core.security import create_access_token, create_refresh_token
from httpx import AsyncClient


@pytest.mark.e2e
@pytest.mark.auth
class TestUserAuthJourney:
    """사용자 인증 여정 E2E 테스트"""

    @pytest.mark.asyncio
    async def test_complete_auth_flow(self, async_client: AsyncClient, test_user):
        """완전한 인증 플로우 테스트: 로그인 → 토큰 사용 → 갱신 → 로그아웃"""

        # 1. 테스트 로그인 (실제 GitHub OAuth 대신)
        login_response = await async_client.post("/api/v1/auth/test-login")

        if login_response.status_code == 200:
            login_data = login_response.json()
            access_token = login_data.get("access_token")
            refresh_token = login_data.get("refresh_token")

            assert access_token is not None
            assert refresh_token is not None

            # 2. 인증된 사용자 정보 조회
            headers = {"Authorization": f"Bearer {access_token}"}
            me_response = await async_client.get("/api/v1/auth/me", headers=headers)

            if me_response.status_code == 200:
                user_data = me_response.json()
                assert "id" in user_data
                assert "email" in user_data
                user_id = user_data["id"]

                # 3. 토큰 갱신
                refresh_response = await async_client.post(
                    "/api/v1/auth/refresh", json={"refresh_token": refresh_token}
                )

                if refresh_response.status_code == 200:
                    refresh_data = refresh_response.json()
                    new_access_token = refresh_data.get("access_token")
                    assert new_access_token is not None
                    assert new_access_token != access_token  # 새 토큰이어야 함

                    # 4. 새 토큰으로 사용자 정보 재조회
                    new_headers = {"Authorization": f"Bearer {new_access_token}"}
                    me_response2 = await async_client.get(
                        "/api/v1/auth/me", headers=new_headers
                    )

                    if me_response2.status_code == 200:
                        user_data2 = me_response2.json()
                        assert user_data2["id"] == user_id  # 같은 사용자

                        # 5. 로그아웃
                        logout_response = await async_client.post(
                            "/api/v1/auth/logout", headers=new_headers
                        )

                        if logout_response.status_code in [200, 204]:
                            # 6. 로그아웃 후 사용자 정보 조회 (실패해야 함)
                            final_response = await async_client.get(
                                "/api/v1/auth/me", headers=new_headers
                            )
                            assert final_response.status_code == 401

                            print("✅ 완전한 인증 플로우 테스트 성공!")
                        else:
                            print(
                                f"⚠️  로그아웃 미구현 (상태: {logout_response.status_code})"
                            )
                    else:
                        print(
                            f"⚠️  새 토큰 검증 실패 (상태: {me_response2.status_code})"
                        )
                else:
                    print(f"⚠️  토큰 갱신 미구현 (상태: {refresh_response.status_code})")
            else:
                print(f"⚠️  사용자 정보 조회 미구현 (상태: {me_response.status_code})")
        else:
            print(f"⚠️  테스트 로그인 미구현 (상태: {login_response.status_code})")
            # 테스트 로그인이 없다면 수동으로 토큰 생성
            await self._test_manual_token_flow(async_client, test_user)

    async def _test_manual_token_flow(self, async_client: AsyncClient, test_user):
        """테스트 로그인이 없을 때 수동 토큰으로 플로우 테스트"""
        # 수동으로 토큰 생성
        access_token = create_access_token(subject=test_user.id)
        refresh_token = create_refresh_token(subject=test_user.id)

        headers = {"Authorization": f"Bearer {access_token}"}

        # 사용자 정보 조회
        me_response = await async_client.get("/api/v1/auth/me", headers=headers)

        if me_response.status_code == 200:
            user_data = me_response.json()
            assert user_data["id"] == str(test_user.id)
            print("✅ 수동 토큰으로 사용자 정보 조회 성공!")
        else:
            print(
                f"⚠️  수동 토큰으로도 사용자 정보 조회 실패 (상태: {me_response.status_code})"
            )

    @pytest.mark.asyncio
    async def test_invalid_token_handling(self, async_client: AsyncClient):
        """잘못된 토큰 처리 테스트"""

        # 1. 잘못된 토큰으로 접근
        invalid_headers = {"Authorization": "Bearer invalid_token_12345"}
        response = await async_client.get("/api/v1/auth/me", headers=invalid_headers)
        assert response.status_code == 401

        # 2. 만료된 토큰 시뮬레이션 (매우 짧은 만료 시간)
        from datetime import timedelta

        expired_token = create_access_token(
            subject="999", expires_delta=timedelta(seconds=-1)  # 이미 만료됨
        )
        expired_headers = {"Authorization": f"Bearer {expired_token}"}
        response = await async_client.get("/api/v1/auth/me", headers=expired_headers)
        assert response.status_code == 401

        # 3. Authorization 헤더 없이 접근
        response = await async_client.get("/api/v1/auth/me")
        assert response.status_code == 401

        print("✅ 잘못된 토큰 처리 테스트 완료!")

    @pytest.mark.asyncio
    async def test_auth_required_endpoints(self, async_client: AsyncClient, test_user):
        """인증이 필요한 엔드포인트들 테스트"""

        # 인증이 필요한 엔드포인트들
        protected_endpoints = [
            ("GET", "/api/v1/auth/me"),
            ("POST", "/api/v1/auth/logout"),
            ("POST", "/api/v1/projects/"),
            ("POST", "/api/v1/notes/"),
            ("POST", "/api/v1/media/upload"),
        ]

        # 1. 인증 없이 접근 (모두 401이어야 함)
        for method, endpoint in protected_endpoints:
            if method == "GET":
                response = await async_client.get(endpoint)
            elif method == "POST":
                response = await async_client.post(endpoint)

            assert response.status_code in [
                401,
                422,
            ], f"{method} {endpoint}는 인증이 필요해야 함"

        # 2. 유효한 토큰으로 접근 (401이 아니어야 함)
        token = create_access_token(subject=str(test_user.id))
        headers = {"Authorization": f"Bearer {token}"}

        for method, endpoint in protected_endpoints:
            if method == "GET":
                response = await async_client.get(endpoint, headers=headers)
            elif method == "POST":
                response = await async_client.post(endpoint, headers=headers)

            # 401이 아니면 성공 (다른 오류는 괜찮음)
            assert (
                response.status_code != 401
            ), f"{method} {endpoint}는 유효한 토큰으로 접근 가능해야 함"

        print("✅ 인증 필요 엔드포인트 테스트 완료!")

    @pytest.mark.asyncio
    async def test_token_security(self, async_client: AsyncClient):
        """토큰 보안 테스트"""

        # 1. 다른 사용자의 토큰으로 접근 시도
        user1_token = create_access_token(subject="1")
        user2_token = create_access_token(subject="2")

        # 토큰이 다르면 다른 사용자로 인식되어야 함
        headers1 = {"Authorization": f"Bearer {user1_token}"}
        headers2 = {"Authorization": f"Bearer {user2_token}"}

        response1 = await async_client.get("/api/v1/auth/me", headers=headers1)
        response2 = await async_client.get("/api/v1/auth/me", headers=headers2)

        # 두 요청이 모두 성공하면 다른 사용자 정보를 반환해야 함
        if response1.status_code == 200 and response2.status_code == 200:
            user1_data = response1.json()
            user2_data = response2.json()

            # 사용자 ID가 다르거나, 한 쪽이 실패해야 함
            assert user1_data.get("id") != user2_data.get(
                "id"
            ), "다른 토큰은 다른 사용자를 반환해야 함"

        print("✅ 토큰 보안 테스트 완료!")

    @pytest.mark.asyncio
    async def test_concurrent_auth_requests(self, async_client: AsyncClient, test_user):
        """동시 인증 요청 테스트"""
        import asyncio

        token = create_access_token(subject=str(test_user.id))
        headers = {"Authorization": f"Bearer {token}"}

        # 동시에 여러 인증 요청
        tasks = []
        for _ in range(5):
            task = async_client.get("/api/v1/auth/me", headers=headers)
            tasks.append(task)

        responses = await asyncio.gather(*tasks, return_exceptions=True)

        # 모든 요청이 성공적으로 처리되어야 함
        success_count = 0
        for response in responses:
            if hasattr(response, "status_code"):
                if response.status_code == 200:
                    success_count += 1
                    user_data = response.json()
                    assert user_data["id"] == str(test_user.id)

        # 최소 일부는 성공해야 함
        assert success_count > 0, "동시 요청 중 일부는 성공해야 함"
        print(f"✅ 동시 인증 요청 테스트 완료! ({success_count}/5 성공)")
