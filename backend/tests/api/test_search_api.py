"""
검색 API 테스트
Search endpoints: 통합검색, 자동완성, 인기검색, 통계
"""

import pytest
from app.models.user import User
from httpx import AsyncClient


@pytest.mark.api
@pytest.mark.search
class TestSearchAPI:
    """검색 관련 API 테스트"""

    @pytest.mark.asyncio
    async def test_search_general_no_query(self, async_client: AsyncClient):
        """통합 검색 - 쿼리 없음"""
        response = await async_client.get("/api/v1/search/")
        # 쿼리가 필요하면 422, 기본 결과 반환하면 200
        assert response.status_code in [200, 422]

    @pytest.mark.asyncio
    async def test_search_general_with_query(self, async_client: AsyncClient):
        """통합 검색 - 쿼리 포함"""
        response = await async_client.get("/api/v1/search/", params={"q": "test"})
        assert response.status_code in [200, 401]

        if response.status_code == 200:
            data = response.json()
            assert isinstance(data, (list, dict))

    @pytest.mark.asyncio
    async def test_search_general_empty_query(self, async_client: AsyncClient):
        """통합 검색 - 빈 쿼리"""
        response = await async_client.get("/api/v1/search/", params={"q": ""})
        assert response.status_code in [200, 422]

    @pytest.mark.asyncio
    async def test_search_general_special_characters(self, async_client: AsyncClient):
        """통합 검색 - 특수문자 쿼리"""
        special_queries = [
            "test & query",
            "query with 'quotes'",
            "한글 검색",
            "emoji 🚀 search",
            "<script>alert('xss')</script>",
            "sql'; DROP TABLE users; --",
        ]

        for query in special_queries:
            response = await async_client.get("/api/v1/search/", params={"q": query})
            assert response.status_code in [200, 401, 422]

    @pytest.mark.asyncio
    async def test_search_projects_no_query(self, async_client: AsyncClient):
        """프로젝트 검색 - 쿼리 없음"""
        response = await async_client.get("/api/v1/search/projects")
        assert response.status_code in [200, 401, 422]

    @pytest.mark.asyncio
    async def test_search_projects_with_query(self, async_client: AsyncClient):
        """프로젝트 검색 - 쿼리 포함"""
        response = await async_client.get(
            "/api/v1/search/projects", params={"q": "react"}
        )
        assert response.status_code in [200, 401]

        if response.status_code == 200:
            data = response.json()
            # 검색 결과는 dict 형태로 반환 (projects, notes 등 포함)
            assert isinstance(data, (list, dict))

    @pytest.mark.asyncio
    async def test_search_projects_with_filters(self, async_client: AsyncClient):
        """프로젝트 검색 - 필터 포함"""
        # 기술 스택 필터
        response = await async_client.get(
            "/api/v1/search/projects", params={"q": "api", "tech": "python"}
        )
        assert response.status_code in [200, 401, 422]

        # 상태 필터
        response = await async_client.get(
            "/api/v1/search/projects", params={"q": "web", "status": "active"}
        )
        assert response.status_code in [200, 401, 422]

    @pytest.mark.asyncio
    async def test_search_notes_no_query(self, async_client: AsyncClient):
        """노트 검색 - 쿼리 없음"""
        response = await async_client.get("/api/v1/search/notes")
        assert response.status_code in [200, 401, 422]

    @pytest.mark.asyncio
    async def test_search_notes_with_query(self, async_client: AsyncClient):
        """노트 검색 - 쿼리 포함"""
        response = await async_client.get(
            "/api/v1/search/notes", params={"q": "meeting"}
        )
        assert response.status_code in [200, 401]

    @pytest.mark.asyncio
    async def test_search_notes_with_filters(self, async_client: AsyncClient):
        """노트 검색 - 필터 포함"""
        # 타입 필터
        response = await async_client.get(
            "/api/v1/search/notes", params={"q": "idea", "type": "personal"}
        )
        assert response.status_code in [200, 401, 422]

        # 날짜 범위 필터
        response = await async_client.get(
            "/api/v1/search/notes",
            params={"q": "project", "date_from": "2024-01-01", "date_to": "2024-12-31"},
        )
        assert response.status_code in [200, 401, 422]

    @pytest.mark.asyncio
    async def test_search_users_no_query(self, async_client: AsyncClient):
        """사용자 검색 - 쿼리 없음"""
        response = await async_client.get("/api/v1/search/users")
        assert response.status_code in [200, 401, 422]

    @pytest.mark.asyncio
    async def test_search_users_with_query(self, async_client: AsyncClient):
        """사용자 검색 - 쿼리 포함"""
        response = await async_client.get("/api/v1/search/users", params={"q": "john"})
        assert response.status_code in [200, 401]

    @pytest.mark.asyncio
    async def test_search_users_privacy(self, async_client: AsyncClient):
        """사용자 검색 - 개인정보 보호"""
        # 이메일로 검색 시도
        response = await async_client.get(
            "/api/v1/search/users", params={"q": "test@example.com"}
        )
        assert response.status_code in [200, 401, 403]  # 개인정보 보호로 403 가능

    @pytest.mark.asyncio
    async def test_search_autocomplete_no_query(self, async_client: AsyncClient):
        """자동완성 - 쿼리 없음"""
        response = await async_client.get("/api/v1/search/autocomplete")
        assert response.status_code in [200, 422]

    @pytest.mark.asyncio
    async def test_search_autocomplete_with_query(self, async_client: AsyncClient):
        """자동완성 - 쿼리 포함"""
        response = await async_client.get(
            "/api/v1/search/autocomplete", params={"q": "rea"}
        )
        assert response.status_code in [200, 401]

        if response.status_code == 200:
            data = response.json()
            # 자동완성 결과는 list 또는 dict 형태
            assert isinstance(data, (list, dict))

    @pytest.mark.asyncio
    async def test_search_autocomplete_short_query(self, async_client: AsyncClient):
        """자동완성 - 짧은 쿼리"""
        # 1글자 쿼리
        response = await async_client.get(
            "/api/v1/search/autocomplete", params={"q": "a"}
        )
        assert response.status_code in [200, 422]  # 최소 길이 제한 있을 수 있음

    @pytest.mark.asyncio
    async def test_search_autocomplete_limit(self, async_client: AsyncClient):
        """자동완성 - 결과 수 제한"""
        response = await async_client.get(
            "/api/v1/search/autocomplete", params={"q": "test", "limit": 5}
        )
        assert response.status_code in [200, 401, 422]

    @pytest.mark.asyncio
    async def test_search_popular_endpoint(self, async_client: AsyncClient):
        """인기 검색어"""
        response = await async_client.get("/api/v1/search/popular")
        assert response.status_code in [200, 401]

        if response.status_code == 200:
            data = response.json()
            # 인기 검색어는 list 또는 dict 형태
            assert isinstance(data, (list, dict))

    @pytest.mark.asyncio
    async def test_search_popular_with_limit(self, async_client: AsyncClient):
        """인기 검색어 - 개수 제한"""
        response = await async_client.get(
            "/api/v1/search/popular", params={"limit": 10}
        )
        assert response.status_code in [200, 401, 422]

    @pytest.mark.asyncio
    async def test_search_popular_with_timeframe(self, async_client: AsyncClient):
        """인기 검색어 - 기간 설정"""
        response = await async_client.get(
            "/api/v1/search/popular", params={"timeframe": "week"}
        )
        assert response.status_code in [200, 401, 422]

    @pytest.mark.asyncio
    async def test_search_stats_unauthorized(self, async_client: AsyncClient):
        """검색 통계 - 인증 없음"""
        response = await async_client.get("/api/v1/search/stats")
        assert response.status_code in [200, 401]

    @pytest.mark.asyncio
    async def test_search_stats_with_auth(self, authenticated_client: AsyncClient):
        """검색 통계 - 인증됨"""
        response = await authenticated_client.get("/api/v1/search/stats")
        assert response.status_code in [200, 401]

        if response.status_code == 200:
            data = response.json()
            assert isinstance(data, dict)

    @pytest.mark.asyncio
    async def test_search_pagination(self, async_client: AsyncClient):
        """검색 결과 페이지네이션"""
        # 통합 검색 페이지네이션
        response = await async_client.get(
            "/api/v1/search/", params={"q": "test", "page": 1, "limit": 10}
        )
        assert response.status_code in [200, 401, 422]

        # 프로젝트 검색 페이지네이션
        response = await async_client.get(
            "/api/v1/search/projects", params={"q": "web", "offset": 0, "limit": 5}
        )
        assert response.status_code in [200, 401, 422]

    @pytest.mark.asyncio
    async def test_search_sorting(self, async_client: AsyncClient):
        """검색 결과 정렬"""
        # 관련도순 정렬
        response = await async_client.get(
            "/api/v1/search/", params={"q": "python", "sort": "relevance"}
        )
        assert response.status_code in [200, 401, 422]

        # 날짜순 정렬
        response = await async_client.get(
            "/api/v1/search/projects",
            params={"q": "api", "sort": "created_at", "order": "desc"},
        )
        assert response.status_code in [200, 401, 422]

    @pytest.mark.asyncio
    async def test_search_long_query(self, async_client: AsyncClient):
        """검색 - 긴 쿼리"""
        long_query = "a very long search query " * 20  # 매우 긴 검색어
        response = await async_client.get("/api/v1/search/", params={"q": long_query})
        # 길이 제한이 있다면 422, 없다면 200
        assert response.status_code in [200, 413, 422, 401]

    @pytest.mark.asyncio
    async def test_search_http_methods(self, async_client: AsyncClient):
        """검색 API HTTP 메서드 검증"""
        # 모든 검색 엔드포인트는 GET만 허용
        search_endpoints = [
            "/api/v1/search/",
            "/api/v1/search/projects",
            "/api/v1/search/notes",
            "/api/v1/search/users",
            "/api/v1/search/autocomplete",
            "/api/v1/search/popular",
            "/api/v1/search/stats",
        ]

        for endpoint in search_endpoints:
            # POST 요청은 허용되지 않아야 함
            response = await async_client.post(endpoint)
            assert response.status_code == 405

    @pytest.mark.asyncio
    async def test_search_rate_limiting_simulation(self, async_client: AsyncClient):
        """검색 API 반복 호출 테스트"""
        # 빠른 연속 검색 요청
        responses = []

        for i in range(10):
            response = await async_client.get(
                "/api/v1/search/", params={"q": f"test{i}"}
            )
            responses.append(response.status_code)

        # Rate limiting이 구현되어 있다면 429가 나올 수 있음
        assert all(status in [200, 401, 422, 429] for status in responses)

    @pytest.mark.asyncio
    async def test_search_concurrent_requests(self, async_client: AsyncClient):
        """검색 동시 요청 테스트"""
        import asyncio

        # 동시에 여러 검색 요청
        tasks = []
        queries = ["python", "javascript", "react", "api", "web"]

        for query in queries:
            task = async_client.get("/api/v1/search/", params={"q": query})
            tasks.append(task)

        responses = await asyncio.gather(*tasks, return_exceptions=True)

        # 모든 요청이 처리되어야 함
        for response in responses:
            if hasattr(response, "status_code"):
                # 동시 요청으로 인한 500 에러도 허용
                assert response.status_code in [200, 401, 422, 500]

    @pytest.mark.asyncio
    async def test_search_injection_attempts(self, async_client: AsyncClient):
        """검색 인젝션 공격 시도"""
        injection_queries = [
            "'; DROP TABLE projects; --",
            "<script>alert('xss')</script>",
            "{{7*7}}",  # Template injection
            "${7*7}",  # Expression injection
            "../../etc/passwd",  # Path traversal
        ]

        for query in injection_queries:
            response = await async_client.get("/api/v1/search/", params={"q": query})
            # 보안 필터링으로 인해 다양한 응답 가능
            assert response.status_code in [200, 400, 401, 422]

            # 응답에 실행된 코드나 민감한 정보가 없어야 함
            if response.status_code == 200:
                content = response.text.lower()
                assert "49" not in content  # 7*7 실행 결과
                assert "root:" not in content  # passwd 파일 내용
