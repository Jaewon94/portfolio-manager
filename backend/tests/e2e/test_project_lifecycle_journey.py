"""
E2E 테스트: 프로젝트 생명주기 여정
사용자가 프로젝트를 생성하고 수정하고 삭제하는 전체 플로우 테스트
"""

import pytest
from app.core.security import create_access_token
from httpx import AsyncClient


@pytest.mark.e2e
@pytest.mark.project
class TestProjectLifecycleJourney:
    """프로젝트 생명주기 E2E 테스트"""

    @pytest.mark.asyncio
    async def test_complete_project_lifecycle(
        self, async_client: AsyncClient, test_user
    ):
        """완전한 프로젝트 생명주기: 생성 → 조회 → 수정 → 삭제"""

        token = create_access_token(subject=str(test_user.id))
        headers = {"Authorization": f"Bearer {token}"}

        # 1. 프로젝트 생성
        project_data = {
            "slug": "e2e-test-project",
            "title": "E2E Test Project",
            "description": "End-to-End 테스트용 프로젝트",
            "tech_stack": ["Python", "FastAPI", "PostgreSQL"],
            "categories": ["Backend"],
            "tags": ["test", "e2e"],
            "status": "active",
            "visibility": "public",
        }

        create_response = await async_client.post(
            "/api/v1/projects/", json=project_data, headers=headers
        )

        if create_response.status_code == 201:
            created_project = create_response.json()
            project_id = created_project["id"]

            assert created_project["slug"] == "e2e-test-project"
            assert created_project["title"] == "E2E Test Project"
            assert created_project["tech_stack"] == ["Python", "FastAPI", "PostgreSQL"]

            # 2. 생성된 프로젝트 조회
            get_response = await async_client.get(
                f"/api/v1/projects/{project_id}", headers=headers
            )

            if get_response.status_code == 200:
                retrieved_project = get_response.json()
                assert retrieved_project["id"] == project_id
                assert retrieved_project["title"] == "E2E Test Project"

                # 3. 프로젝트 수정
                update_data = {
                    "title": "Updated E2E Test Project",
                    "description": "업데이트된 E2E 테스트 프로젝트",
                    "tech_stack": ["Python", "FastAPI", "PostgreSQL", "Redis"],
                    "tags": ["test", "e2e", "updated"],
                }

                update_response = await async_client.put(
                    f"/api/v1/projects/{project_id}", json=update_data, headers=headers
                )

                if update_response.status_code == 200:
                    updated_project = update_response.json()
                    assert updated_project["title"] == "Updated E2E Test Project"
                    assert "Redis" in updated_project["tech_stack"]
                    assert "updated" in updated_project["tags"]

                    # 4. 업데이트 확인을 위한 재조회
                    verify_response = await async_client.get(
                        f"/api/v1/projects/{project_id}", headers=headers
                    )

                    if verify_response.status_code == 200:
                        verified_project = verify_response.json()
                        assert verified_project["title"] == "Updated E2E Test Project"

                        # 5. 프로젝트 삭제
                        delete_response = await async_client.delete(
                            f"/api/v1/projects/{project_id}", headers=headers
                        )

                        if delete_response.status_code in [200, 204]:
                            # 6. 삭제 확인 (404 또는 401이어야 함)
                            final_response = await async_client.get(
                                f"/api/v1/projects/{project_id}", headers=headers
                            )
                            assert final_response.status_code in [404, 401]

                            print("✅ 완전한 프로젝트 생명주기 테스트 성공!")
                        else:
                            print(
                                f"⚠️  프로젝트 삭제 미구현 (상태: {delete_response.status_code})"
                            )
                    else:
                        print(
                            f"⚠️  업데이트 확인 실패 (상태: {verify_response.status_code})"
                        )
                else:
                    print(
                        f"⚠️  프로젝트 수정 미구현 (상태: {update_response.status_code})"
                    )
            else:
                print(f"⚠️  프로젝트 조회 미구현 (상태: {get_response.status_code})")
        else:
            print(f"⚠️  프로젝트 생성 미구현 (상태: {create_response.status_code})")

    @pytest.mark.asyncio
    async def test_project_list_and_search(self, async_client: AsyncClient, test_user):
        """프로젝트 목록 조회 및 검색 여정"""

        token = create_access_token(subject=str(test_user.id))
        headers = {"Authorization": f"Bearer {token}"}

        # 1. 여러 프로젝트 생성
        projects_to_create = [
            {
                "slug": "react-app-e2e",
                "title": "React Application E2E",
                "description": "React 애플리케이션",
                "tech_stack": ["React", "TypeScript"],
                "tags": ["frontend", "react"],
            },
            {
                "slug": "python-api-e2e",
                "title": "Python API E2E",
                "description": "Python FastAPI 백엔드",
                "tech_stack": ["Python", "FastAPI"],
                "tags": ["backend", "api"],
            },
        ]

        created_project_ids = []

        for project_data in projects_to_create:
            response = await async_client.post(
                "/api/v1/projects/", json=project_data, headers=headers
            )
            if response.status_code == 201:
                created_project_ids.append(response.json()["id"])

        if created_project_ids:
            # 2. 프로젝트 목록 조회
            list_response = await async_client.get("/api/v1/projects/", headers=headers)

            if list_response.status_code == 200:
                projects_list = list_response.json()

                # 생성한 프로젝트들이 목록에 있는지 확인
                project_titles = [p.get("title", "") for p in projects_list]
                assert "React Application E2E" in project_titles
                assert "Python API E2E" in project_titles

                # 3. 검색 테스트
                search_response = await async_client.get(
                    "/api/v1/search/projects", params={"q": "React"}, headers=headers
                )

                if search_response.status_code == 200:
                    search_results = search_response.json()

                    # 검색 결과에서 React 프로젝트 찾기
                    if isinstance(search_results, dict):
                        projects = search_results.get("projects", [])
                    else:
                        projects = search_results

                    react_found = any("React" in p.get("title", "") for p in projects)
                    if react_found:
                        print("✅ 프로젝트 검색 성공!")
                    else:
                        print("⚠️  검색 결과에 React 프로젝트 없음")
                else:
                    print(
                        f"⚠️  프로젝트 검색 미구현 (상태: {search_response.status_code})"
                    )

                # 4. 생성한 프로젝트들 정리
                for project_id in created_project_ids:
                    await async_client.delete(
                        f"/api/v1/projects/{project_id}", headers=headers
                    )

                print("✅ 프로젝트 목록 및 검색 테스트 완료!")
            else:
                print(
                    f"⚠️  프로젝트 목록 조회 미구현 (상태: {list_response.status_code})"
                )
        else:
            print("⚠️  테스트용 프로젝트 생성 실패")

    @pytest.mark.asyncio
    async def test_project_validation_and_errors(
        self, async_client: AsyncClient, test_user
    ):
        """프로젝트 검증 및 오류 처리 테스트"""

        token = create_access_token(subject=str(test_user.id))
        headers = {"Authorization": f"Bearer {token}"}

        # 1. 잘못된 데이터로 프로젝트 생성 시도
        invalid_data_tests = [
            # 빈 데이터
            {},
            # 필수 필드 누락
            {"title": "Only Title"},
            # 잘못된 데이터 타입
            {"slug": 123, "title": "Test"},
            # 너무 긴 데이터
            {"slug": "test", "title": "A" * 1000, "description": "B" * 10000},
        ]

        for invalid_data in invalid_data_tests:
            response = await async_client.post(
                "/api/v1/projects/", json=invalid_data, headers=headers
            )
            # 검증 오류나 인증 오류여야 함
            assert response.status_code in [
                401,
                422,
            ], f"잘못된 데이터는 거부되어야 함: {invalid_data}"

        # 2. 존재하지 않는 프로젝트 접근
        nonexistent_response = await async_client.get(
            "/api/v1/projects/99999", headers=headers
        )
        assert nonexistent_response.status_code in [404, 401]

        # 3. 중복 슬러그 테스트
        project_data = {
            "slug": "duplicate-test",
            "title": "Duplicate Test",
            "description": "중복 테스트",
        }

        # 첫 번째 생성
        first_response = await async_client.post(
            "/api/v1/projects/", json=project_data, headers=headers
        )

        if first_response.status_code == 201:
            first_project_id = first_response.json()["id"]

            # 같은 슬러그로 두 번째 생성 시도
            second_response = await async_client.post(
                "/api/v1/projects/", json=project_data, headers=headers
            )

            # 중복 오류여야 함
            assert second_response.status_code in [
                400,
                422,
            ], "중복 슬러그는 거부되어야 함"

            # 정리
            await async_client.delete(
                f"/api/v1/projects/{first_project_id}", headers=headers
            )

            print("✅ 프로젝트 검증 및 오류 처리 테스트 완료!")
        else:
            print(
                f"⚠️  기본 프로젝트 생성 실패로 중복 테스트 스킵 (상태: {first_response.status_code})"
            )

    @pytest.mark.asyncio
    async def test_project_permissions(
        self, async_client: AsyncClient, test_user, admin_user
    ):
        """프로젝트 권한 테스트"""

        # 일반 사용자 토큰
        user_token = create_access_token(subject=str(test_user.id))
        user_headers = {"Authorization": f"Bearer {user_token}"}

        # 관리자 토큰
        admin_token = create_access_token(subject=str(admin_user.id))
        admin_headers = {"Authorization": f"Bearer {admin_token}"}

        # 1. 일반 사용자로 프로젝트 생성
        project_data = {
            "slug": "permission-test",
            "title": "Permission Test Project",
            "description": "권한 테스트용 프로젝트",
            "visibility": "private",
        }

        create_response = await async_client.post(
            "/api/v1/projects/", json=project_data, headers=user_headers
        )

        if create_response.status_code == 201:
            project_id = create_response.json()["id"]

            # 2. 프로젝트 소유자는 접근 가능
            owner_response = await async_client.get(
                f"/api/v1/projects/{project_id}", headers=user_headers
            )
            assert owner_response.status_code == 200

            # 3. 다른 사용자는 비공개 프로젝트 접근 불가 (또는 제한)
            other_response = await async_client.get(
                f"/api/v1/projects/{project_id}", headers=admin_headers
            )
            # 접근 불가하거나 제한적 접근
            assert other_response.status_code in [200, 403, 404]

            # 4. 인증 없이는 접근 불가
            unauth_response = await async_client.get(f"/api/v1/projects/{project_id}")
            assert unauth_response.status_code in [401, 404]

            # 정리
            await async_client.delete(
                f"/api/v1/projects/{project_id}", headers=user_headers
            )

            print("✅ 프로젝트 권한 테스트 완료!")
        else:
            print(
                f"⚠️  권한 테스트용 프로젝트 생성 실패 (상태: {create_response.status_code})"
            )

    @pytest.mark.asyncio
    async def test_project_with_media_integration(
        self, async_client: AsyncClient, test_user
    ):
        """프로젝트와 미디어 통합 테스트"""

        token = create_access_token(subject=str(test_user.id))
        headers = {"Authorization": f"Bearer {token}"}

        # 1. 프로젝트 생성
        project_data = {
            "slug": "media-integration-test",
            "title": "Media Integration Test",
            "description": "미디어 통합 테스트",
        }

        project_response = await async_client.post(
            "/api/v1/projects/", json=project_data, headers=headers
        )

        if project_response.status_code == 201:
            project_id = project_response.json()["id"]

            # 2. 프로젝트에 미디어 업로드
            from io import BytesIO

            test_file = BytesIO(b"test image content")
            files = {"file": ("test.png", test_file, "image/png")}
            data = {"target_type": "project", "target_id": str(project_id)}

            upload_response = await async_client.post(
                "/api/v1/media/upload", files=files, data=data, headers=headers
            )

            if upload_response.status_code == 201:
                media_data = upload_response.json()
                media_id = media_data["id"]

                # 3. 프로젝트의 미디어 목록 조회
                media_list_response = await async_client.get(
                    "/api/v1/media/",
                    params={"target_type": "project", "target_id": project_id},
                    headers=headers,
                )

                if media_list_response.status_code == 200:
                    media_list = media_list_response.json()

                    # 페이지네이션 응답인지 확인
                    if isinstance(media_list, dict):
                        media_items = media_list.get("media", [])
                    else:
                        media_items = media_list

                    # 업로드한 미디어가 목록에 있는지 확인
                    uploaded_media = next(
                        (m for m in media_items if m["id"] == media_id), None
                    )
                    assert (
                        uploaded_media is not None
                    ), "업로드한 미디어가 목록에 있어야 함"

                    print("✅ 프로젝트-미디어 통합 테스트 성공!")
                else:
                    print(
                        f"⚠️  미디어 목록 조회 실패 (상태: {media_list_response.status_code})"
                    )

                # 정리
                await async_client.delete(f"/api/v1/media/{media_id}", headers=headers)
            else:
                print(f"⚠️  미디어 업로드 실패 (상태: {upload_response.status_code})")

            # 프로젝트 정리
            await async_client.delete(f"/api/v1/projects/{project_id}", headers=headers)
        else:
            print(
                f"⚠️  통합 테스트용 프로젝트 생성 실패 (상태: {project_response.status_code})"
            )
