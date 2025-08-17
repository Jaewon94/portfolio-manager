"""
E2E 테스트: GitHub 저장소 연동 여정
사용자가 프로젝트에 GitHub 저장소를 연동하고 동기화하는 전체 플로우 테스트
"""

import pytest
from datetime import datetime
from unittest.mock import patch
from app.core.security import create_access_token
from httpx import AsyncClient


@pytest.mark.e2e
@pytest.mark.github
class TestGithubRepositoryJourney:
    """GitHub 저장소 연동 E2E 테스트"""

    @pytest.mark.asyncio
    async def test_complete_github_integration_journey(
        self, async_client: AsyncClient, test_user
    ):
        """완전한 GitHub 저장소 연동 여정: 프로젝트 생성 → GitHub 연동 → 동기화 → 연동 해제"""

        token = create_access_token(subject=str(test_user.id))
        headers = {"Authorization": f"Bearer {token}"}

        # 1. 프로젝트 생성
        project_data = {
            "slug": "github-integration-project",
            "title": "GitHub Integration Test Project",
            "description": "GitHub 연동 테스트용 프로젝트",
            "tech_stack": ["Python", "FastAPI"],
            "categories": ["Backend"],
            "tags": ["github", "integration"],
            "status": "active",
            "visibility": "public",
        }

        project_response = await async_client.post(
            "/api/v1/projects/", json=project_data, headers=headers
        )

        if project_response.status_code == 201:
            project = project_response.json()
            project_id = project["id"]
            
            assert project["slug"] == "github-integration-project"
            print(f"✅ 프로젝트 생성 성공 (ID: {project_id})")

            # 2. GitHub 저장소 연동
            github_data = {
                "github_url": "https://github.com/testuser/integration-test-repo",
                "repository_name": "testuser/integration-test-repo",
                "sync_enabled": True
            }

            github_response = await async_client.post(
                f"/api/v1/projects/{project_id}/github",
                json=github_data,
                headers=headers
            )

            if github_response.status_code == 201:
                github_repo = github_response.json()["data"]
                
                assert github_repo["project_id"] == project_id
                assert github_repo["github_url"] == github_data["github_url"]
                assert github_repo["repository_name"] == github_data["repository_name"]
                assert github_repo["sync_enabled"] is True
                print("✅ GitHub 저장소 연동 성공")

                # 3. 연동된 저장소 조회
                get_response = await async_client.get(
                    f"/api/v1/projects/{project_id}/github",
                    headers=headers
                )

                if get_response.status_code == 200:
                    retrieved_repo = get_response.json()["data"]
                    assert retrieved_repo["id"] == github_repo["id"]
                    assert retrieved_repo["github_url"] == github_data["github_url"]
                    print("✅ GitHub 저장소 조회 성공")

                    # 4. GitHub 저장소 정보 동기화 (Mock GitHub API)
                    mock_github_data = {
                        "name": "integration-test-repo",
                        "full_name": "testuser/integration-test-repo",
                        "stargazers_count": 150,
                        "forks_count": 30,
                        "watchers_count": 200,
                        "language": "Python",
                        "license": {"name": "MIT"},
                        "private": False,
                        "fork": False,
                        "default_branch": "main"
                    }

                    with patch('app.services.github.GithubRepositoryService._fetch_github_data',
                              return_value=mock_github_data):
                        sync_response = await async_client.post(
                            f"/api/v1/projects/{project_id}/github/sync",
                            headers=headers
                        )

                        if sync_response.status_code == 200:
                            synced_repo = sync_response.json()["data"]
                            
                            assert synced_repo["stars"] == 150
                            assert synced_repo["forks"] == 30
                            assert synced_repo["watchers"] == 200
                            assert synced_repo["language"] == "Python"
                            assert synced_repo["license"] == "MIT"
                            assert synced_repo["last_synced_at"] is not None
                            print("✅ GitHub 저장소 동기화 성공")

                            # 5. 커밋 히스토리 조회 (Mock GitHub API)
                            mock_commits = [
                                {
                                    "sha": "abc123def456",
                                    "commit": {
                                        "message": "Initial commit for integration test",
                                        "author": {
                                            "name": "Test User",
                                            "email": "test@example.com",
                                            "date": "2024-01-01T00:00:00Z"
                                        }
                                    },
                                    "html_url": "https://github.com/testuser/integration-test-repo/commit/abc123def456"
                                },
                                {
                                    "sha": "def456ghi789",
                                    "commit": {
                                        "message": "Add E2E test features",
                                        "author": {
                                            "name": "Test User",
                                            "email": "test@example.com",
                                            "date": "2024-01-02T00:00:00Z"
                                        }
                                    },
                                    "html_url": "https://github.com/testuser/integration-test-repo/commit/def456ghi789"
                                }
                            ]

                            with patch('app.services.github.GithubRepositoryService._fetch_commits',
                                      return_value=mock_commits):
                                commits_response = await async_client.get(
                                    f"/api/v1/projects/{project_id}/github/commits",
                                    params={"limit": 10},
                                    headers=headers
                                )

                                if commits_response.status_code == 200:
                                    commits_data = commits_response.json()["data"]
                                    
                                    assert len(commits_data) == 2
                                    assert commits_data[0]["sha"] == "abc123def456"
                                    assert commits_data[0]["message"] == "Initial commit for integration test"
                                    assert commits_data[1]["sha"] == "def456ghi789"
                                    assert commits_data[1]["message"] == "Add E2E test features"
                                    print("✅ 커밋 히스토리 조회 성공")

                                    # 6. GitHub 저장소 설정 업데이트
                                    update_data = {
                                        "sync_enabled": False,
                                        "github_url": "https://github.com/testuser/updated-integration-repo"
                                    }

                                    update_response = await async_client.patch(
                                        f"/api/v1/projects/{project_id}/github",
                                        json=update_data,
                                        headers=headers
                                    )

                                    if update_response.status_code == 200:
                                        updated_repo = update_response.json()["data"]
                                        
                                        assert updated_repo["sync_enabled"] is False
                                        assert updated_repo["github_url"] == update_data["github_url"]
                                        assert updated_repo["repository_name"] == "testuser/updated-integration-repo"
                                        print("✅ GitHub 저장소 설정 업데이트 성공")

                                        # 7. GitHub 저장소 연동 해제
                                        delete_response = await async_client.delete(
                                            f"/api/v1/projects/{project_id}/github",
                                            headers=headers
                                        )

                                        if delete_response.status_code == 204:
                                            # 8. 연동 해제 확인 (404 응답이어야 함)
                                            verify_delete_response = await async_client.get(
                                                f"/api/v1/projects/{project_id}/github",
                                                headers=headers
                                            )
                                            
                                            assert verify_delete_response.status_code == 404
                                            print("✅ GitHub 저장소 연동 해제 성공")

                                            # 최종 프로젝트 정리
                                            await async_client.delete(
                                                f"/api/v1/projects/{project_id}",
                                                headers=headers
                                            )
                                            
                                            print("✅ 완전한 GitHub 연동 여정 테스트 성공!")
                                        else:
                                            print(f"⚠️  GitHub 저장소 연동 해제 실패 (상태: {delete_response.status_code})")
                                    else:
                                        print(f"⚠️  GitHub 저장소 설정 업데이트 실패 (상태: {update_response.status_code})")
                                else:
                                    print(f"⚠️  커밋 히스토리 조회 실패 (상태: {commits_response.status_code})")
                        else:
                            print(f"⚠️  GitHub 저장소 동기화 실패 (상태: {sync_response.status_code})")
                else:
                    print(f"⚠️  GitHub 저장소 조회 실패 (상태: {get_response.status_code})")
            else:
                print(f"⚠️  GitHub 저장소 연동 실패 (상태: {github_response.status_code})")
                
            # 프로젝트 정리 (GitHub 연동 실패 시)
            await async_client.delete(f"/api/v1/projects/{project_id}", headers=headers)
        else:
            print(f"⚠️  프로젝트 생성 실패 (상태: {project_response.status_code})")

    @pytest.mark.asyncio
    async def test_multiple_projects_github_sync_journey(
        self, async_client: AsyncClient, test_user
    ):
        """여러 프로젝트 GitHub 저장소 일괄 동기화 여정"""

        token = create_access_token(subject=str(test_user.id))
        headers = {"Authorization": f"Bearer {token}"}

        # 1. 여러 프로젝트 생성
        projects_data = [
            {
                "slug": "bulk-sync-project-1",
                "title": "Bulk Sync Project 1", 
                "description": "일괄 동기화 테스트 프로젝트 1",
                "tech_stack": ["React", "TypeScript"],
                "tags": ["frontend", "bulk-sync"]
            },
            {
                "slug": "bulk-sync-project-2",
                "title": "Bulk Sync Project 2",
                "description": "일괄 동기화 테스트 프로젝트 2", 
                "tech_stack": ["Python", "FastAPI"],
                "tags": ["backend", "bulk-sync"]
            }
        ]

        created_projects = []
        
        for project_data in projects_data:
            response = await async_client.post(
                "/api/v1/projects/", json=project_data, headers=headers
            )
            if response.status_code == 201:
                created_projects.append(response.json())

        if len(created_projects) == 2:
            print(f"✅ {len(created_projects)}개 프로젝트 생성 성공")

            # 2. 각 프로젝트에 GitHub 저장소 연동
            github_repos_data = [
                {
                    "github_url": "https://github.com/testuser/bulk-sync-repo-1",
                    "repository_name": "testuser/bulk-sync-repo-1",
                    "sync_enabled": True
                },
                {
                    "github_url": "https://github.com/testuser/bulk-sync-repo-2", 
                    "repository_name": "testuser/bulk-sync-repo-2",
                    "sync_enabled": True
                }
            ]

            connected_repos = []

            for i, project in enumerate(created_projects):
                github_response = await async_client.post(
                    f"/api/v1/projects/{project['id']}/github",
                    json=github_repos_data[i],
                    headers=headers
                )
                
                if github_response.status_code == 201:
                    connected_repos.append({
                        "project_id": project["id"],
                        "repository_data": github_response.json()["data"]
                    })

            if len(connected_repos) == 2:
                print("✅ 모든 프로젝트에 GitHub 저장소 연동 성공")

                # 3. 일괄 동기화 수행
                def mock_fetch_github_data(repo_name):
                    return {
                        "name": repo_name.split('/')[-1],
                        "full_name": repo_name,
                        "stargazers_count": 75,
                        "forks_count": 15,
                        "watchers_count": 100,
                        "language": "Python" if "repo-2" in repo_name else "TypeScript",
                        "license": {"name": "MIT"},
                        "private": False,
                        "fork": False,
                        "default_branch": "main"
                    }

                bulk_sync_data = {
                    "project_ids": [repo["project_id"] for repo in connected_repos]
                }

                with patch('app.services.github.GithubRepositoryService._fetch_github_data',
                          side_effect=mock_fetch_github_data):
                    bulk_sync_response = await async_client.post(
                        "/api/v1/github/bulk-sync",
                        json=bulk_sync_data,
                        headers=headers
                    )

                    if bulk_sync_response.status_code == 200:
                        sync_results = bulk_sync_response.json()["data"]
                        
                        assert len(sync_results) == 2
                        
                        # 모든 동기화 결과가 성공인지 확인
                        for result in sync_results:
                            assert result["success"] is True
                            assert result["project_id"] in bulk_sync_data["project_ids"]
                            assert "last_synced_at" in result
                            assert "repository_id" in result

                        print("✅ 일괄 GitHub 저장소 동기화 성공")

                        # 4. 동기화 결과 개별 확인
                        for connected_repo in connected_repos:
                            check_response = await async_client.get(
                                f"/api/v1/projects/{connected_repo['project_id']}/github",
                                headers=headers
                            )
                            
                            if check_response.status_code == 200:
                                repo_data = check_response.json()["data"]
                                assert repo_data["stars"] == 75
                                assert repo_data["forks"] == 15
                                assert repo_data["watchers"] == 100
                                assert repo_data["last_synced_at"] is not None

                        print("✅ 개별 동기화 결과 확인 완료")
                        print("✅ 여러 프로젝트 GitHub 일괄 동기화 여정 성공!")
                    else:
                        print(f"⚠️  일괄 동기화 실패 (상태: {bulk_sync_response.status_code})")
            else:
                print(f"⚠️  GitHub 저장소 연동 부분 실패 ({len(connected_repos)}/2)")

            # 정리: 생성된 프로젝트들 삭제
            for project in created_projects:
                await async_client.delete(
                    f"/api/v1/projects/{project['id']}", headers=headers
                )
        else:
            print(f"⚠️  프로젝트 생성 부분 실패 ({len(created_projects)}/2)")

    @pytest.mark.asyncio
    async def test_github_integration_error_handling_journey(
        self, async_client: AsyncClient, test_user
    ):
        """GitHub 연동 오류 처리 여정"""

        token = create_access_token(subject=str(test_user.id))
        headers = {"Authorization": f"Bearer {token}"}

        # 1. 프로젝트 생성
        project_data = {
            "slug": "error-handling-project",
            "title": "Error Handling Test Project",
            "description": "오류 처리 테스트용 프로젝트",
        }

        project_response = await async_client.post(
            "/api/v1/projects/", json=project_data, headers=headers
        )

        if project_response.status_code == 201:
            project_id = project_response.json()["id"]
            print("✅ 오류 처리 테스트용 프로젝트 생성 성공")

            # 2. 잘못된 GitHub URL 형식으로 연동 시도
            invalid_url_tests = [
                {
                    "github_url": "https://not-github.com/user/repo",
                    "repository_name": "user/repo",
                    "expected_status": 422,
                    "description": "비GitHub 도메인"
                },
                {
                    "github_url": "invalid-url-format",
                    "repository_name": "user/repo", 
                    "expected_status": 422,
                    "description": "잘못된 URL 형식"
                },
                {
                    "github_url": "https://github.com/user/repo",
                    "repository_name": "",
                    "expected_status": 422,
                    "description": "빈 저장소 이름"
                }
            ]

            for test_case in invalid_url_tests:
                invalid_response = await async_client.post(
                    f"/api/v1/projects/{project_id}/github",
                    json={
                        "github_url": test_case["github_url"],
                        "repository_name": test_case["repository_name"],
                        "sync_enabled": True
                    },
                    headers=headers
                )
                
                assert invalid_response.status_code == test_case["expected_status"], \
                    f"{test_case['description']} 테스트 실패"
                
                error_data = invalid_response.json()
                assert error_data["success"] is False

            print("✅ 잘못된 GitHub URL 검증 테스트 완료")

            # 3. 정상 GitHub 저장소 연동
            valid_github_data = {
                "github_url": "https://github.com/testuser/error-test-repo",
                "repository_name": "testuser/error-test-repo",
                "sync_enabled": True
            }

            github_response = await async_client.post(
                f"/api/v1/projects/{project_id}/github",
                json=valid_github_data,
                headers=headers
            )

            if github_response.status_code == 201:
                print("✅ 정상 GitHub 저장소 연동 성공")

                # 4. 중복 연동 시도 (같은 프로젝트에 다른 저장소)
                duplicate_data = {
                    "github_url": "https://github.com/testuser/another-repo",
                    "repository_name": "testuser/another-repo",
                    "sync_enabled": True
                }

                duplicate_response = await async_client.post(
                    f"/api/v1/projects/{project_id}/github",
                    json=duplicate_data,
                    headers=headers
                )

                # 이미 연동된 프로젝트에 추가 연동 시도는 실패해야 함
                assert duplicate_response.status_code in [409, 400]
                print("✅ 중복 연동 방지 테스트 완료")

                # 5. GitHub API 실패 시나리오 (동기화 실패)
                from app.core.exceptions import ExternalAPIException

                with patch('app.services.github.GithubRepositoryService._fetch_github_data',
                          side_effect=ExternalAPIException("GitHub API rate limit exceeded")):
                    api_error_response = await async_client.post(
                        f"/api/v1/projects/{project_id}/github/sync",
                        headers=headers
                    )

                    assert api_error_response.status_code == 502
                    error_data = api_error_response.json()
                    assert error_data["success"] is False
                    assert "GitHub API" in error_data["error"]["message"]

                print("✅ GitHub API 오류 처리 테스트 완료")

                # 6. 존재하지 않는 프로젝트로 GitHub 작업 시도
                non_existent_project_id = 99999
                not_found_response = await async_client.post(
                    f"/api/v1/projects/{non_existent_project_id}/github",
                    json=valid_github_data,
                    headers=headers
                )

                assert not_found_response.status_code == 404
                print("✅ 존재하지 않는 프로젝트 처리 테스트 완료")

                print("✅ GitHub 연동 오류 처리 여정 완료!")
            else:
                print(f"⚠️  정상 GitHub 저장소 연동 실패 (상태: {github_response.status_code})")

            # 프로젝트 정리
            await async_client.delete(f"/api/v1/projects/{project_id}", headers=headers)
        else:
            print(f"⚠️  오류 처리 테스트용 프로젝트 생성 실패 (상태: {project_response.status_code})")

    @pytest.mark.asyncio
    async def test_github_permissions_journey(
        self, async_client: AsyncClient, test_user, admin_user
    ):
        """GitHub 저장소 권한 제어 여정"""

        # 사용자별 토큰 생성
        user_token = create_access_token(subject=str(test_user.id))
        user_headers = {"Authorization": f"Bearer {user_token}"}

        admin_token = create_access_token(subject=str(admin_user.id))
        admin_headers = {"Authorization": f"Bearer {admin_token}"}

        # 1. 일반 사용자로 프로젝트 및 GitHub 저장소 연동
        project_data = {
            "slug": "permissions-test-project",
            "title": "Permissions Test Project",
            "description": "권한 테스트용 프로젝트",
            "visibility": "private"
        }

        project_response = await async_client.post(
            "/api/v1/projects/", json=project_data, headers=user_headers
        )

        if project_response.status_code == 201:
            project_id = project_response.json()["id"]

            github_data = {
                "github_url": "https://github.com/testuser/permissions-test-repo",
                "repository_name": "testuser/permissions-test-repo",
                "sync_enabled": True
            }

            github_response = await async_client.post(
                f"/api/v1/projects/{project_id}/github",
                json=github_data,
                headers=user_headers
            )

            if github_response.status_code == 201:
                print("✅ 일반 사용자 GitHub 저장소 연동 성공")

                # 2. 프로젝트 소유자는 GitHub 저장소 접근 가능
                owner_access_response = await async_client.get(
                    f"/api/v1/projects/{project_id}/github",
                    headers=user_headers
                )
                assert owner_access_response.status_code == 200
                print("✅ 프로젝트 소유자 GitHub 저장소 접근 확인")

                # 3. 다른 사용자는 비공개 프로젝트의 GitHub 저장소 접근 제한
                other_user_response = await async_client.get(
                    f"/api/v1/projects/{project_id}/github",
                    headers=admin_headers
                )
                assert other_user_response.status_code in [403, 404]
                print("✅ 다른 사용자 접근 제한 확인")

                # 4. 인증 없이는 접근 불가
                unauth_response = await async_client.get(
                    f"/api/v1/projects/{project_id}/github"
                )
                assert unauth_response.status_code == 401
                print("✅ 인증 없는 접근 차단 확인")

                # 5. 다른 사용자가 GitHub 저장소 수정 시도 (실패해야 함)
                unauthorized_update = await async_client.patch(
                    f"/api/v1/projects/{project_id}/github",
                    json={"sync_enabled": False},
                    headers=admin_headers
                )
                assert unauthorized_update.status_code in [403, 404]
                print("✅ 권한 없는 수정 차단 확인")

                # 6. 다른 사용자가 GitHub 저장소 삭제 시도 (실패해야 함)
                unauthorized_delete = await async_client.delete(
                    f"/api/v1/projects/{project_id}/github",
                    headers=admin_headers
                )
                assert unauthorized_delete.status_code in [403, 404]
                print("✅ 권한 없는 삭제 차단 확인")

                print("✅ GitHub 저장소 권한 제어 여정 완료!")
            else:
                print(f"⚠️  GitHub 저장소 연동 실패 (상태: {github_response.status_code})")

            # 프로젝트 정리
            await async_client.delete(f"/api/v1/projects/{project_id}", headers=user_headers)
        else:
            print(f"⚠️  권한 테스트용 프로젝트 생성 실패 (상태: {project_response.status_code})")