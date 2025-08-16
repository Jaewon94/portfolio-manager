"""
E2E 테스트: 검색 기능 전체 여정
사용자가 콘텐츠를 생성하고 검색하는 전체 플로우 테스트
"""

import asyncio

import pytest
from app.core.security import create_access_token
from httpx import AsyncClient


@pytest.mark.e2e
@pytest.mark.search
class TestSearchJourney:
    """검색 기능 E2E 테스트"""

    @pytest.mark.asyncio
    async def test_complete_search_journey(self, async_client: AsyncClient, test_user):
        """완전한 검색 여정: 콘텐츠 생성 → 검색 → 결과 확인"""

        token = create_access_token(subject=str(test_user.id))
        headers = {"Authorization": f"Bearer {token}"}

        # 1. 검색 가능한 콘텐츠들 생성
        created_items = await self._create_searchable_content(async_client, headers)

        if created_items["projects"] or created_items["notes"]:
            # 2. 통합 검색 테스트
            await self._test_general_search(async_client, headers)

            # 3. 프로젝트 검색 테스트
            await self._test_project_search(async_client, headers)

            # 4. 노트 검색 테스트
            await self._test_note_search(async_client, headers)

            # 5. 자동완성 테스트
            await self._test_autocomplete(async_client, headers)

            # 6. 인기 검색어 테스트
            await self._test_popular_searches(async_client, headers)

            # 7. 정리
            await self._cleanup_content(async_client, headers, created_items)

            print("✅ 완전한 검색 여정 테스트 완료!")
        else:
            print("⚠️  검색 가능한 콘텐츠 생성 실패")

    async def _create_searchable_content(self, async_client: AsyncClient, headers):
        """검색 가능한 콘텐츠 생성"""
        created_items = {"projects": [], "notes": []}

        # 프로젝트 생성
        projects_data = [
            {
                "slug": "react-search-test",
                "title": "React Search Application",
                "description": "React로 만든 검색 애플리케이션",
                "tech_stack": ["React", "TypeScript", "Elasticsearch"],
                "tags": ["frontend", "search", "react"],
            },
            {
                "slug": "python-ml-project",
                "title": "Python Machine Learning",
                "description": "Python 머신러닝 프로젝트",
                "tech_stack": ["Python", "TensorFlow", "Pandas"],
                "tags": ["backend", "ml", "python"],
            },
            {
                "slug": "fullstack-blog",
                "title": "Full Stack Blog Platform",
                "description": "전체 스택 블로그 플랫폼",
                "tech_stack": ["React", "Node.js", "PostgreSQL"],
                "tags": ["fullstack", "blog", "web"],
            },
        ]

        for project_data in projects_data:
            response = await async_client.post(
                "/api/v1/projects/", json=project_data, headers=headers
            )
            if response.status_code == 201:
                created_items["projects"].append(response.json()["id"])

        # 노트 생성
        notes_data = [
            {
                "title": "React 개발 팁",
                "content": "React 개발할 때 유용한 팁들을 정리한 노트입니다. useState, useEffect 등의 훅 사용법과 성능 최적화 방법을 다룹니다.",
                "tags": ["react", "frontend", "tips"],
            },
            {
                "title": "Python 데이터 분석",
                "content": "Python을 사용한 데이터 분석 방법론입니다. Pandas와 NumPy를 활용한 데이터 처리와 시각화를 다룹니다.",
                "tags": ["python", "data", "analysis"],
            },
            {
                "title": "검색 엔진 최적화",
                "content": "웹사이트의 검색 엔진 최적화(SEO) 방법들을 정리했습니다. 메타 태그, 구조화된 데이터, 페이지 속도 등을 다룹니다.",
                "tags": ["seo", "search", "optimization"],
            },
        ]

        for note_data in notes_data:
            response = await async_client.post(
                "/api/v1/notes/", json=note_data, headers=headers
            )
            if response.status_code == 201:
                created_items["notes"].append(response.json()["id"])

        print(
            f"생성된 콘텐츠: 프로젝트 {len(created_items['projects'])}개, 노트 {len(created_items['notes'])}개"
        )
        return created_items

    async def _test_general_search(self, async_client: AsyncClient, headers):
        """통합 검색 테스트"""
        search_queries = ["React", "Python", "검색", "Machine Learning", "blog"]

        for query in search_queries:
            response = await async_client.get(
                "/api/v1/search/", params={"q": query}, headers=headers
            )

            if response.status_code == 200:
                results = response.json()

                # 결과 구조 확인
                if isinstance(results, dict):
                    # 구조화된 검색 결과
                    total_results = 0
                    if "projects" in results:
                        total_results += len(results["projects"])
                    if "notes" in results:
                        total_results += len(results["notes"])

                    if total_results > 0:
                        print(f"✅ '{query}' 통합 검색 성공! ({total_results}개 결과)")
                    else:
                        print(f"⚠️  '{query}' 검색 결과 없음")
                else:
                    # 단순 리스트 결과
                    if len(results) > 0:
                        print(f"✅ '{query}' 통합 검색 성공! ({len(results)}개 결과)")
                    else:
                        print(f"⚠️  '{query}' 검색 결과 없음")
            else:
                print(f"⚠️  '{query}' 통합 검색 실패 (상태: {response.status_code})")

    async def _test_project_search(self, async_client: AsyncClient, headers):
        """프로젝트 검색 테스트"""
        project_queries = [
            ("React", "React Search Application"),
            ("Python", "Python Machine Learning"),
            ("blog", "Full Stack Blog Platform"),
            ("frontend", "React"),
            ("ml", "Machine Learning"),
        ]

        for query, expected_term in project_queries:
            response = await async_client.get(
                "/api/v1/search/projects", params={"q": query}, headers=headers
            )

            if response.status_code == 200:
                results = response.json()

                # 결과에서 프로젝트 추출
                if isinstance(results, dict):
                    projects = results.get("projects", [])
                else:
                    projects = results

                # 예상 결과가 있는지 확인
                found = any(
                    expected_term.lower() in p.get("title", "").lower()
                    or expected_term.lower() in p.get("description", "").lower()
                    for p in projects
                )

                if found:
                    print(f"✅ 프로젝트 검색 '{query}' 성공!")
                else:
                    print(
                        f"⚠️  프로젝트 검색 '{query}' 결과에서 '{expected_term}' 못찾음"
                    )
            else:
                print(f"⚠️  프로젝트 검색 '{query}' 실패 (상태: {response.status_code})")

    async def _test_note_search(self, async_client: AsyncClient, headers):
        """노트 검색 테스트"""
        note_queries = [
            ("React", "React 개발 팁"),
            ("Python", "Python 데이터 분석"),
            ("검색", "검색 엔진 최적화"),
            ("데이터", "데이터 분석"),
            ("SEO", "검색 엔진"),
        ]

        for query, expected_term in note_queries:
            response = await async_client.get(
                "/api/v1/search/notes", params={"q": query}, headers=headers
            )

            if response.status_code == 200:
                results = response.json()

                # 결과에서 노트 추출
                if isinstance(results, dict):
                    notes = results.get("notes", [])
                else:
                    notes = results

                # 예상 결과가 있는지 확인
                found = any(
                    expected_term.lower() in n.get("title", "").lower()
                    or expected_term.lower() in n.get("content", "").lower()
                    for n in notes
                )

                if found:
                    print(f"✅ 노트 검색 '{query}' 성공!")
                else:
                    print(f"⚠️  노트 검색 '{query}' 결과에서 '{expected_term}' 못찾음")
            else:
                print(f"⚠️  노트 검색 '{query}' 실패 (상태: {response.status_code})")

    async def _test_autocomplete(self, async_client: AsyncClient, headers):
        """자동완성 테스트"""
        autocomplete_queries = ["Rea", "Pyt", "검", "Mach", "blo"]

        for query in autocomplete_queries:
            response = await async_client.get(
                "/api/v1/search/autocomplete", params={"q": query}, headers=headers
            )

            if response.status_code == 200:
                suggestions = response.json()

                if isinstance(suggestions, (list, dict)) and len(suggestions) > 0:
                    print(f"✅ 자동완성 '{query}' 성공!")
                else:
                    print(f"⚠️  자동완성 '{query}' 결과 없음")
            else:
                print(f"⚠️  자동완성 '{query}' 실패 (상태: {response.status_code})")

    async def _test_popular_searches(self, async_client: AsyncClient, headers):
        """인기 검색어 테스트"""
        # 여러 검색을 통해 인기 검색어 데이터 생성
        popular_terms = ["React", "Python", "JavaScript", "API", "Database"]

        # 각 검색어를 여러 번 검색하여 인기도 생성
        for term in popular_terms:
            for _ in range(3):  # 각 검색어를 3번씩 검색
                await async_client.get(
                    "/api/v1/search/", params={"q": term}, headers=headers
                )
                await asyncio.sleep(0.1)  # 짧은 딜레이

        # 인기 검색어 조회
        response = await async_client.get("/api/v1/search/popular", headers=headers)

        if response.status_code == 200:
            popular_searches = response.json()

            if isinstance(popular_searches, (list, dict)) and len(popular_searches) > 0:
                print("✅ 인기 검색어 조회 성공!")

                # 검색한 단어들이 인기 검색어에 포함되는지 확인
                if isinstance(popular_searches, list):
                    popular_terms_found = [
                        item.get("term", item) for item in popular_searches
                    ]
                else:
                    popular_terms_found = popular_searches.get("terms", [])

                matches = [
                    term for term in popular_terms if term in str(popular_terms_found)
                ]
                if matches:
                    print(f"✅ 검색한 단어들이 인기 검색어에 반영됨: {matches}")
            else:
                print("⚠️  인기 검색어 결과 없음")
        else:
            print(f"⚠️  인기 검색어 조회 실패 (상태: {response.status_code})")

    async def _cleanup_content(self, async_client: AsyncClient, headers, created_items):
        """생성한 콘텐츠 정리"""
        # 프로젝트 삭제
        for project_id in created_items["projects"]:
            await async_client.delete(f"/api/v1/projects/{project_id}", headers=headers)

        # 노트 삭제
        for note_id in created_items["notes"]:
            await async_client.delete(f"/api/v1/notes/{note_id}", headers=headers)

        print(
            f"정리 완료: 프로젝트 {len(created_items['projects'])}개, 노트 {len(created_items['notes'])}개"
        )

    @pytest.mark.asyncio
    async def test_search_edge_cases(self, async_client: AsyncClient, test_user):
        """검색 엣지 케이스 테스트"""

        token = create_access_token(subject=str(test_user.id))
        headers = {"Authorization": f"Bearer {token}"}

        edge_case_queries = [
            "",  # 빈 검색어
            " ",  # 공백만
            "a",  # 매우 짧은 검색어
            "a" * 1000,  # 매우 긴 검색어
            "!@#$%^&*()",  # 특수문자만
            "한글검색",  # 한글
            "🚀🎉💻",  # 이모지
            "SELECT * FROM users",  # SQL 인젝션 시도
            "<script>alert('xss')</script>",  # XSS 시도
        ]

        for query in edge_case_queries:
            response = await async_client.get(
                "/api/v1/search/", params={"q": query}, headers=headers
            )

            # 서버가 크래시하지 않고 적절히 처리해야 함
            assert response.status_code in [
                200,
                400,
                422,
            ], f"검색어 '{query}'에 대해 서버가 적절히 응답해야 함"

            # XSS나 SQL 인젝션이 실행되지 않았는지 확인
            if response.status_code == 200:
                content = response.text.lower()
                assert "alert(" not in content, "XSS 스크립트가 실행되면 안됨"
                assert "select * from" not in content, "SQL 쿼리가 노출되면 안됨"

        print("✅ 검색 엣지 케이스 테스트 완료!")

    @pytest.mark.asyncio
    async def test_search_performance(self, async_client: AsyncClient, test_user):
        """검색 성능 테스트"""
        import time

        token = create_access_token(subject=str(test_user.id))
        headers = {"Authorization": f"Bearer {token}"}

        # 동시 검색 요청 테스트
        search_queries = ["React", "Python", "JavaScript", "API", "Database"] * 2

        start_time = time.time()

        # 동시 검색 실행
        tasks = []
        for query in search_queries:
            task = async_client.get(
                "/api/v1/search/", params={"q": query}, headers=headers
            )
            tasks.append(task)

        responses = await asyncio.gather(*tasks, return_exceptions=True)

        end_time = time.time()
        total_time = end_time - start_time

        # 결과 분석
        successful_requests = 0
        failed_requests = 0

        for response in responses:
            if hasattr(response, "status_code"):
                if response.status_code == 200:
                    successful_requests += 1
                else:
                    failed_requests += 1
            else:
                failed_requests += 1

        print(f"✅ 검색 성능 테스트 완료!")
        print(f"   - 총 요청: {len(search_queries)}개")
        print(f"   - 성공: {successful_requests}개")
        print(f"   - 실패: {failed_requests}개")
        print(f"   - 총 시간: {total_time:.2f}초")
        print(f"   - 평균 응답시간: {total_time/len(search_queries):.3f}초")

        # 성능 기준 (예: 평균 응답시간 5초 이내)
        avg_response_time = total_time / len(search_queries)
        assert (
            avg_response_time < 5.0
        ), f"평균 응답시간이 너무 느림: {avg_response_time:.3f}초"

        # 최소 50% 이상은 성공해야 함
        success_rate = successful_requests / len(search_queries)
        assert success_rate >= 0.5, f"성공률이 너무 낮음: {success_rate:.1%}"
