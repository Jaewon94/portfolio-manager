"""
검색 API 테스트
PostgreSQL full-text search, 자동완성, 인기 검색어 기능 테스트
"""

import pytest
from httpx import AsyncClient
from unittest.mock import patch, AsyncMock

from app.main import app


class TestSearchAPI:
    """검색 API 테스트 클래스"""

    @pytest.mark.asyncio
    async def test_search_api_basic(self):
        """기본 검색 API 엔드포인트 테스트"""
        async with AsyncClient(app=app, base_url="http://test") as client:
            response = await client.get("/api/v1/search/", params={"q": "test"})
            
            # 에러 응답일 경우 상세 출력
            if response.status_code != 200:
                print(f"Response status: {response.status_code}")
                print(f"Response content: {response.text}")
                print(f"Response headers: {response.headers}")
            
            # API 응답 구조 검증 (실제 데이터 없어도 구조는 확인 가능)
            assert response.status_code == 200
            data = response.json()
            
            assert "projects" in data
            assert "notes" in data
            assert "users" in data
            assert "total_count" in data
            assert "query" in data
            assert data["query"] == "test"
            assert isinstance(data["projects"], list)
            assert isinstance(data["notes"], list)
            assert isinstance(data["users"], list)
            assert isinstance(data["total_count"], int)

    @pytest.mark.asyncio
    async def test_search_projects_only(self):
        """프로젝트만 검색 테스트"""
        async with AsyncClient(app=app, base_url="http://test") as client:
            response = await client.get("/api/v1/search/projects", params={"q": "test"})
            
            assert response.status_code == 200
            data = response.json()
            
            # 프로젝트만 검색 시 notes, users는 빈 배열이어야 함
            assert "projects" in data
            assert "notes" in data
            assert "users" in data
            assert len(data["notes"]) == 0
            assert len(data["users"]) == 0

    @pytest.mark.asyncio
    async def test_search_notes_only(self):
        """노트만 검색 테스트"""
        async with AsyncClient(app=app, base_url="http://test") as client:
            response = await client.get("/api/v1/search/notes", params={"q": "test"})
            
            assert response.status_code == 200
            data = response.json()
            
            # 노트만 검색 시 projects, users는 빈 배열이어야 함
            assert "projects" in data
            assert "notes" in data
            assert "users" in data
            assert len(data["projects"]) == 0
            assert len(data["users"]) == 0

    @pytest.mark.asyncio
    async def test_search_users_only(self):
        """사용자만 검색 테스트"""
        async with AsyncClient(app=app, base_url="http://test") as client:
            response = await client.get("/api/v1/search/users", params={"q": "test"})
            
            assert response.status_code == 200
            data = response.json()
            
            # 사용자만 검색 시 projects, notes는 빈 배열이어야 함
            assert "projects" in data
            assert "notes" in data
            assert "users" in data
            assert len(data["projects"]) == 0
            assert len(data["notes"]) == 0

    @pytest.mark.asyncio
    async def test_autocomplete_api(self):
        """자동완성 API 테스트"""
        async with AsyncClient(app=app, base_url="http://test") as client:
            response = await client.get("/api/v1/search/autocomplete", params={"q": "te"})
            
            assert response.status_code == 200
            data = response.json()
            
            assert "query" in data
            assert "suggestions" in data
            assert "type" in data
            assert data["query"] == "te"
            assert data["type"] == "all"
            assert isinstance(data["suggestions"], list)

    @pytest.mark.asyncio
    async def test_autocomplete_by_type(self):
        """타입별 자동완성 테스트"""
        async with AsyncClient(app=app, base_url="http://test") as client:
            response = await client.get(
                "/api/v1/search/autocomplete",
                params={"q": "te", "type": "project"}
            )
            
            assert response.status_code == 200
            data = response.json()
            assert data["type"] == "project"

    @pytest.mark.asyncio
    async def test_autocomplete_invalid_type(self):
        """잘못된 자동완성 타입 테스트"""
        async with AsyncClient(app=app, base_url="http://test") as client:
            response = await client.get(
                "/api/v1/search/autocomplete",
                params={"q": "test", "type": "invalid"}
            )
            
            assert response.status_code == 400
            data = response.json()
            assert "Invalid autocomplete type" in data["detail"]

    @pytest.mark.asyncio
    async def test_popular_searches(self):
        """인기 검색어 조회 테스트"""
        async with AsyncClient(app=app, base_url="http://test") as client:
            response = await client.get("/api/v1/search/popular")
            
            assert response.status_code == 200
            data = response.json()
            
            assert "popular_searches" in data
            assert "limit" in data
            assert isinstance(data["popular_searches"], list)
            assert data["limit"] == 10
            
            # 인기 검색어 구조 확인 (빈 배열이어도 구조는 확인)
            for item in data["popular_searches"]:
                assert "keyword" in item
                assert "count" in item
                assert isinstance(item["count"], int)

    @pytest.mark.asyncio
    async def test_popular_searches_limit(self):
        """인기 검색어 제한 테스트"""
        async with AsyncClient(app=app, base_url="http://test") as client:
            response = await client.get("/api/v1/search/popular", params={"limit": 5})
            
            assert response.status_code == 200
            data = response.json()
            
            assert data["limit"] == 5
            assert len(data["popular_searches"]) <= 5

    @pytest.mark.asyncio
    async def test_search_stats(self):
        """검색 통계 조회 테스트"""
        async with AsyncClient(app=app, base_url="http://test") as client:
            response = await client.get("/api/v1/search/stats")
            
            assert response.status_code == 200
            data = response.json()
            
            assert "total_projects" in data
            assert "total_notes" in data
            assert "total_users" in data
            assert "indexable_content" in data
            
            assert isinstance(data["total_projects"], int)
            assert isinstance(data["total_notes"], int)
            assert isinstance(data["total_users"], int)
            assert isinstance(data["indexable_content"], int)
            
            assert data["total_projects"] >= 0
            assert data["total_notes"] >= 0
            assert data["total_users"] >= 0
            
            # indexable_content는 projects + notes 합계
            assert data["indexable_content"] == data["total_projects"] + data["total_notes"]

    @pytest.mark.asyncio
    async def test_search_validation_errors(self):
        """검색 파라미터 검증 테스트"""
        async with AsyncClient(app=app, base_url="http://test") as client:
            # 빈 검색어
            response = await client.get("/api/v1/search/", params={"q": ""})
            assert response.status_code == 422
            
            # 너무 긴 검색어
            long_query = "a" * 101  # 100자 초과
            response = await client.get("/api/v1/search/", params={"q": long_query})
            assert response.status_code == 422
            
            # 음수 limit
            response = await client.get(
                "/api/v1/search/",
                params={"q": "test", "limit": -1}
            )
            assert response.status_code == 422
            
            # 너무 큰 limit
            response = await client.get(
                "/api/v1/search/",
                params={"q": "test", "limit": 101}
            )
            assert response.status_code == 422
            
            # 음수 offset
            response = await client.get(
                "/api/v1/search/",
                params={"q": "test", "offset": -1}
            )
            assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_search_with_filters(self):
        """필터를 사용한 검색 테스트"""
        async with AsyncClient(app=app, base_url="http://test") as client:
            response = await client.get(
                "/api/v1/search/",
                params={
                    "q": "test",
                    "categories": ["Backend"],
                    "content_types": ["project"]
                }
            )
            
            assert response.status_code == 200
            data = response.json()
            
            # 응답 구조 확인
            assert "projects" in data
            assert "notes" in data
            assert "users" in data
            assert isinstance(data["projects"], list)
            assert isinstance(data["notes"], list)
            assert isinstance(data["users"], list)

    @pytest.mark.asyncio
    async def test_search_pagination(self):
        """검색 페이지네이션 테스트"""
        async with AsyncClient(app=app, base_url="http://test") as client:
            # 첫 번째 페이지
            response = await client.get(
                "/api/v1/search/",
                params={"q": "test", "limit": 10, "offset": 0}
            )
            
            assert response.status_code == 200
            data = response.json()
            
            # 두 번째 페이지
            response = await client.get(
                "/api/v1/search/",
                params={"q": "test", "limit": 10, "offset": 10}
            )
            
            assert response.status_code == 200
            data = response.json()

    @pytest.mark.asyncio
    async def test_search_performance_basic(self):
        """기본 성능 테스트 (응답 시간 체크)"""
        import time
        
        async with AsyncClient(app=app, base_url="http://test") as client:
            start_time = time.time()
            response = await client.get("/api/v1/search/", params={"q": "test"})
            end_time = time.time()
            
            assert response.status_code == 200
            
            # 기본적인 성능 확인 (2초 이내 응답 - 관대한 기준)
            response_time = end_time - start_time
            assert response_time < 2.0, f"Search took too long: {response_time:.2f}s"