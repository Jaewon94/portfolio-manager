"""
GitHub 저장소 관리 서비스
TDD Green 단계: 테스트를 통과시키는 최소 구현
"""

import httpx
import re
from typing import Optional, List, Dict, Any
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from app.models.github_repository import GithubRepository
from app.schemas.github import (
    GithubRepositoryCreate,
    GithubRepositoryUpdate,
    GithubRepositorySync,
    GithubCommit,
    GithubRepositoryStats
)
from app.core.exceptions import (
    NotFoundException,
    DuplicateException,
    ValidationException,
    ExternalAPIException
)


class GithubRepositoryService:
    """GitHub 저장소 관리 서비스"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def create_github_repository(
        self,
        project_id: int,
        data: GithubRepositoryCreate
    ) -> GithubRepository:
        """
        프로젝트에 GitHub 저장소 연동
        
        Args:
            project_id: 프로젝트 ID
            data: GitHub 저장소 생성 데이터
            
        Returns:
            GithubRepository: 생성된 GitHub 저장소 정보
            
        Raises:
            DuplicateException: 중복된 GitHub URL
            ValidationException: 잘못된 GitHub URL 형식
        """
        # GitHub URL 형식 검증
        github_url = str(data.github_url)
        if not github_url.startswith('https://github.com/'):
            raise ValidationException("Invalid GitHub URL format")
        
        # 중복 URL 확인
        result = await self.db.execute(
            select(GithubRepository).where(GithubRepository.github_url == github_url)
        )
        existing_repo = result.scalar_one_or_none()
        if existing_repo:
            raise DuplicateException("GitHub URL already exists")
        
        # 새 GitHub 저장소 생성
        github_repo = GithubRepository(
            project_id=project_id,
            github_url=github_url,
            repository_name=data.repository_name or self._extract_repo_name(github_url),
            sync_enabled=data.sync_enabled,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        
        try:
            self.db.add(github_repo)
            await self.db.commit()
            await self.db.refresh(github_repo)
            return github_repo
        except IntegrityError:
            await self.db.rollback()
            raise DuplicateException("GitHub URL already exists")
    
    async def get_by_project_id(self, project_id: int) -> Optional[GithubRepository]:
        """
        프로젝트 ID로 GitHub 저장소 조회
        
        Args:
            project_id: 프로젝트 ID
            
        Returns:
            Optional[GithubRepository]: GitHub 저장소 정보
        """
        result = await self.db.execute(
            select(GithubRepository).where(GithubRepository.project_id == project_id)
        )
        return result.scalar_one_or_none()
    
    async def get_by_id(self, repository_id: int) -> Optional[GithubRepository]:
        """
        ID로 GitHub 저장소 조회
        
        Args:
            repository_id: GitHub 저장소 ID
            
        Returns:
            Optional[GithubRepository]: GitHub 저장소 정보
        """
        result = await self.db.execute(
            select(GithubRepository).where(GithubRepository.id == repository_id)
        )
        return result.scalar_one_or_none()
    
    async def sync_repository(self, repository_id: int) -> GithubRepository:
        """
        GitHub API를 통해 저장소 정보 동기화
        
        Args:
            repository_id: GitHub 저장소 ID
            
        Returns:
            GithubRepository: 동기화된 저장소 정보
            
        Raises:
            NotFoundException: 저장소를 찾을 수 없음
            ExternalAPIException: GitHub API 호출 실패
        """
        # 저장소 조회
        repository = await self.get_by_id(repository_id)
        if not repository:
            raise NotFoundException(f"GitHub repository with ID {repository_id} not found")
        
        try:
            # GitHub API에서 데이터 조회
            github_data = await self._fetch_github_data(repository.repository_name)
            
            # 저장소 정보 업데이트
            repository.stars = github_data.get("stargazers_count", 0)
            repository.forks = github_data.get("forks_count", 0)
            repository.watchers = github_data.get("watchers_count", 0)
            repository.language = github_data.get("language")
            repository.license = github_data.get("license", {}).get("name") if github_data.get("license") else None
            repository.is_private = github_data.get("private", False)
            repository.is_fork = github_data.get("fork", False)
            repository.last_synced_at = datetime.utcnow()
            repository.sync_error_message = None
            repository.updated_at = datetime.utcnow()
            
            await self.db.commit()
            await self.db.refresh(repository)
            return repository
            
        except Exception as e:
            # 동기화 실패 시 에러 메시지 저장
            repository.sync_error_message = str(e)
            repository.last_synced_at = datetime.utcnow()
            repository.updated_at = datetime.utcnow()
            await self.db.commit()
            
            if "API rate limit" in str(e):
                raise ExternalAPIException("GitHub API rate limit exceeded")
            else:
                raise ExternalAPIException(f"Failed to sync GitHub repository: {str(e)}")
    
    async def update_repository(
        self,
        repository_id: int,
        data: GithubRepositoryUpdate
    ) -> GithubRepository:
        """
        GitHub 저장소 정보 업데이트
        
        Args:
            repository_id: GitHub 저장소 ID
            data: 업데이트할 데이터
            
        Returns:
            GithubRepository: 업데이트된 저장소 정보
            
        Raises:
            NotFoundException: 저장소를 찾을 수 없음
        """
        repository = await self.get_by_id(repository_id)
        if not repository:
            raise NotFoundException(f"GitHub repository with ID {repository_id} not found")
        
        # 업데이트 가능한 필드만 수정
        update_data = data.model_dump(exclude_unset=True)
        
        for field, value in update_data.items():
            if field == "github_url" and value:
                # URL 변경 시 중복 확인
                github_url = str(value)
                if not github_url.startswith('https://github.com/'):
                    raise ValidationException("Invalid GitHub URL format")
                
                # 다른 저장소에서 같은 URL 사용하는지 확인
                result = await self.db.execute(
                    select(GithubRepository).where(
                        GithubRepository.github_url == github_url,
                        GithubRepository.id != repository_id
                    )
                )
                existing_repo = result.scalar_one_or_none()
                if existing_repo:
                    raise DuplicateException("GitHub URL already exists")
                
                # URL 변경 시 repository_name도 자동 업데이트
                repository.github_url = github_url
                repository.repository_name = self._extract_repo_name(github_url)
            else:
                setattr(repository, field, value)
        
        repository.updated_at = datetime.utcnow()
        
        try:
            await self.db.commit()
            await self.db.refresh(repository)
            return repository
        except IntegrityError:
            await self.db.rollback()
            raise DuplicateException("GitHub URL already exists")
    
    async def delete_repository(self, repository_id: int) -> bool:
        """
        GitHub 저장소 연동 해제
        
        Args:
            repository_id: GitHub 저장소 ID
            
        Returns:
            bool: 삭제 성공 여부
            
        Raises:
            NotFoundException: 저장소를 찾을 수 없음
        """
        repository = await self.get_by_id(repository_id)
        if not repository:
            raise NotFoundException(f"GitHub repository with ID {repository_id} not found")
        
        await self.db.delete(repository)
        await self.db.commit()
        return True
    
    async def bulk_sync_repositories(
        self,
        project_ids: List[int]
    ) -> List[Dict[str, Any]]:
        """
        여러 GitHub 저장소 일괄 동기화
        
        Args:
            project_ids: 프로젝트 ID 목록
            
        Returns:
            List[Dict[str, Any]]: 동기화 결과 목록
        """
        results = []
        
        for project_id in project_ids:
            try:
                # 프로젝트별 GitHub 저장소 조회
                repository = await self.get_by_project_id(project_id)
                if not repository:
                    results.append({
                        "project_id": project_id,
                        "success": False,
                        "error": "No GitHub repository found for this project"
                    })
                    continue
                
                if not repository.sync_enabled:
                    results.append({
                        "project_id": project_id,
                        "success": False,
                        "error": "Sync is disabled for this repository"
                    })
                    continue
                
                # 저장소 동기화 실행
                await self.sync_repository(repository.id)
                results.append({
                    "project_id": project_id,
                    "repository_id": repository.id,
                    "success": True,
                    "last_synced_at": datetime.utcnow().isoformat()
                })
                
            except Exception as e:
                results.append({
                    "project_id": project_id,
                    "success": False,
                    "error": str(e)
                })
        
        return results
    
    async def get_commit_history(
        self,
        repository_id: int,
        limit: int = 100
    ) -> List[GithubCommit]:
        """
        GitHub 저장소 커밋 히스토리 조회
        
        Args:
            repository_id: GitHub 저장소 ID
            limit: 조회할 커밋 수
            
        Returns:
            List[GithubCommit]: 커밋 히스토리
            
        Raises:
            NotFoundException: 저장소를 찾을 수 없음
            ExternalAPIException: GitHub API 호출 실패
        """
        repository = await self.get_by_id(repository_id)
        if not repository:
            raise NotFoundException(f"GitHub repository with ID {repository_id} not found")
        
        try:
            # GitHub API에서 커밋 데이터 조회
            commits_data = await self._fetch_commits(repository.repository_name, limit)
            
            # GithubCommit 스키마 객체로 변환
            commits = []
            for commit_data in commits_data:
                commit = GithubCommit(
                    sha=commit_data["sha"],
                    message=commit_data["commit"]["message"],
                    author_name=commit_data["commit"]["author"]["name"],
                    author_email=commit_data["commit"]["author"]["email"],
                    date=datetime.fromisoformat(commit_data["commit"]["author"]["date"].replace("Z", "+00:00")),
                    url=commit_data["html_url"]
                )
                commits.append(commit)
            
            return commits
            
        except Exception as e:
            raise ExternalAPIException(f"Failed to fetch commit history: {str(e)}")
    
    async def validate_repository_access(
        self,
        github_url: str,
        access_token: Optional[str] = None
    ) -> bool:
        """
        GitHub 저장소 접근 권한 검증
        
        Args:
            github_url: GitHub 저장소 URL
            access_token: GitHub 액세스 토큰 (선택적)
            
        Returns:
            bool: 접근 가능 여부
        """
        try:
            return await self._check_repository_access(github_url, access_token)
        except Exception:
            return False
    
    async def _fetch_github_data(
        self,
        repository_name: str
    ) -> Dict[str, Any]:
        """
        GitHub API에서 저장소 데이터 조회
        
        Args:
            repository_name: 저장소명 (owner/repo 형식)
            
        Returns:
            Dict[str, Any]: GitHub API 응답 데이터
            
        Raises:
            ExternalAPIException: GitHub API 호출 실패
        """
        try:
            async with httpx.AsyncClient() as client:
                url = f"https://api.github.com/repos/{repository_name}"
                headers = {
                    "Accept": "application/vnd.github.v3+json",
                    "User-Agent": "portfolio-manager/1.0"
                }
                
                response = await client.get(url, headers=headers)
                
                if response.status_code == 200:
                    return response.json()
                elif response.status_code == 404:
                    raise ExternalAPIException(f"Repository {repository_name} not found")
                elif response.status_code == 403:
                    raise ExternalAPIException("GitHub API rate limit exceeded")
                else:
                    raise ExternalAPIException(f"GitHub API error: {response.status_code}")
                    
        except httpx.RequestError as e:
            raise ExternalAPIException(f"Failed to connect to GitHub API: {str(e)}")
    
    async def _fetch_commits(
        self,
        repository_name: str,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """
        GitHub API에서 커밋 데이터 조회
        
        Args:
            repository_name: 저장소명 (owner/repo 형식)
            limit: 조회할 커밋 수
            
        Returns:
            List[Dict[str, Any]]: GitHub 커밋 데이터
            
        Raises:
            ExternalAPIException: GitHub API 호출 실패
        """
        try:
            async with httpx.AsyncClient() as client:
                url = f"https://api.github.com/repos/{repository_name}/commits"
                headers = {
                    "Accept": "application/vnd.github.v3+json",
                    "User-Agent": "portfolio-manager/1.0"
                }
                params = {"per_page": min(limit, 100)}  # GitHub API 최대 100개 제한
                
                response = await client.get(url, headers=headers, params=params)
                
                if response.status_code == 200:
                    return response.json()
                elif response.status_code == 404:
                    raise ExternalAPIException(f"Repository {repository_name} not found")
                elif response.status_code == 403:
                    raise ExternalAPIException("GitHub API rate limit exceeded")
                else:
                    raise ExternalAPIException(f"GitHub API error: {response.status_code}")
                    
        except httpx.RequestError as e:
            raise ExternalAPIException(f"Failed to connect to GitHub API: {str(e)}")
    
    async def _check_repository_access(
        self,
        github_url: str,
        access_token: Optional[str] = None
    ) -> bool:
        """
        GitHub 저장소 접근 권한 확인
        
        Args:
            github_url: GitHub 저장소 URL
            access_token: GitHub 액세스 토큰 (선택적)
            
        Returns:
            bool: 접근 가능 여부
        """
        try:
            # URL에서 repository_name 추출
            repository_name = self._extract_repo_name(github_url)
            
            async with httpx.AsyncClient() as client:
                url = f"https://api.github.com/repos/{repository_name}"
                headers = {
                    "Accept": "application/vnd.github.v3+json",
                    "User-Agent": "portfolio-manager/1.0"
                }
                
                # 액세스 토큰이 있는 경우 Authorization 헤더 추가
                if access_token:
                    headers["Authorization"] = f"token {access_token}"
                
                response = await client.get(url, headers=headers)
                
                # 200: 접근 가능, 404: 존재하지 않거나 비공개, 403: 권한 없음
                return response.status_code == 200
                
        except Exception:
            return False
    
    def _extract_repo_name(self, github_url: str) -> str:
        """
        GitHub URL에서 owner/repo 이름 추출
        
        Args:
            github_url: GitHub 저장소 URL
            
        Returns:
            str: owner/repo 형식의 저장소명
        """
        # https://github.com/owner/repo 또는 https://github.com/owner/repo.git
        pattern = r'github\.com/([^/]+/[^/\.]+)'
        match = re.search(pattern, github_url)
        if match:
            return match.group(1)
        return ""