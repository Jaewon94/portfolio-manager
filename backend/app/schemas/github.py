"""
GitHub 저장소 관련 Pydantic 스키마
"""

from typing import Optional, Dict, Any, List
from datetime import datetime
from pydantic import BaseModel, Field, HttpUrl, field_validator, ConfigDict
import re


class GithubRepositoryBase(BaseModel):
    """GitHub 저장소 기본 스키마"""
    github_url: HttpUrl = Field(..., description="GitHub 저장소 URL")
    sync_enabled: bool = Field(True, description="자동 동기화 활성화 여부")
    
    @field_validator('github_url')
    @classmethod
    def validate_github_url(cls, v):
        """GitHub URL 형식 검증"""
        url_str = str(v)
        if not url_str.startswith('https://github.com/'):
            raise ValueError('URL must be a GitHub repository URL')
        
        # GitHub URL 패턴 검증: https://github.com/owner/repo
        pattern = r'^https://github\.com/[\w.-]+/[\w.-]+(?:\.git)?$'
        if not re.match(pattern, url_str):
            raise ValueError('Invalid GitHub repository URL format')
        
        return v
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "github_url": "https://github.com/username/repository",
                "sync_enabled": True
            }
        }
    )


class GithubRepositoryCreate(GithubRepositoryBase):
    """GitHub 저장소 생성 스키마"""
    repository_name: Optional[str] = Field(None, description="저장소명 (owner/repo 형식)")
    
    @field_validator('repository_name', mode='before')
    @classmethod
    def extract_repository_name(cls, v, info):
        """GitHub URL에서 저장소명 추출"""
        if v:
            return v
        
        # info.data를 통해 다른 필드 값에 접근
        github_url = info.data.get('github_url')
        if github_url:
            url_str = str(github_url)
            # URL에서 owner/repo 추출
            match = re.search(r'github\.com/([^/]+/[^/\.]+)', url_str)
            if match:
                return match.group(1)
        
        return None


class GithubRepositoryUpdate(BaseModel):
    """GitHub 저장소 업데이트 스키마"""
    github_url: Optional[HttpUrl] = None
    sync_enabled: Optional[bool] = None
    
    @field_validator('github_url')
    @classmethod
    def validate_github_url_if_provided(cls, v):
        """GitHub URL이 제공된 경우에만 검증"""
        if v:
            url_str = str(v)
            if not url_str.startswith('https://github.com/'):
                raise ValueError('URL must be a GitHub repository URL')
        return v


class GithubRepositorySync(BaseModel):
    """GitHub 저장소 동기화 결과 스키마"""
    stars: int = Field(0, ge=0)
    forks: int = Field(0, ge=0)
    watchers: int = Field(0, ge=0)
    language: Optional[str] = None
    license: Optional[str] = None
    is_private: bool = False
    is_fork: bool = False
    last_commit_sha: Optional[str] = None
    last_commit_message: Optional[str] = None
    last_commit_date: Optional[datetime] = None
    last_synced_at: datetime = Field(default_factory=datetime.utcnow)
    sync_error_message: Optional[str] = None


class GithubRepository(GithubRepositoryBase):
    """GitHub 저장소 응답 스키마"""
    id: int
    project_id: int
    repository_name: str
    stars: int = 0
    forks: int = 0
    watchers: int = 0
    language: Optional[str] = None
    license: Optional[str] = None
    is_private: bool = False
    is_fork: bool = False
    last_commit_sha: Optional[str] = None
    last_commit_message: Optional[str] = None
    last_commit_date: Optional[datetime] = None
    last_synced_at: Optional[datetime] = None
    sync_error_message: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    
    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": 1,
                "project_id": 1,
                "github_url": "https://github.com/username/repository",
                "repository_name": "username/repository",
                "stars": 100,
                "forks": 20,
                "watchers": 150,
                "language": "Python",
                "license": "MIT",
                "is_private": False,
                "is_fork": False,
                "sync_enabled": True,
                "last_synced_at": "2024-01-01T00:00:00Z",
                "created_at": "2024-01-01T00:00:00Z",
                "updated_at": "2024-01-01T00:00:00Z"
            }
        }
    )


class GithubCommit(BaseModel):
    """GitHub 커밋 정보 스키마"""
    sha: str
    message: str
    author_name: str
    author_email: str
    date: datetime
    url: str
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "sha": "abc123def456",
                "message": "Add new feature",
                "author_name": "John Doe",
                "author_email": "john@example.com",
                "date": "2024-01-01T00:00:00Z",
                "url": "https://github.com/username/repo/commit/abc123def456"
            }
        }
    )


class GithubRepositoryStats(BaseModel):
    """GitHub 저장소 통계 스키마"""
    total_commits: int = 0
    total_contributors: int = 0
    total_issues: int = 0
    total_pull_requests: int = 0
    code_frequency: Optional[List[List[int]]] = None
    commit_activity: Optional[List[Dict[str, Any]]] = None
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "total_commits": 500,
                "total_contributors": 10,
                "total_issues": 50,
                "total_pull_requests": 100
            }
        }
    )


class GithubWebhookPayload(BaseModel):
    """GitHub Webhook 페이로드 스키마"""
    repository: Dict[str, Any]
    action: Optional[str] = None
    sender: Dict[str, Any]
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "repository": {
                    "id": 123456,
                    "name": "repository",
                    "full_name": "username/repository",
                    "private": False
                },
                "action": "opened",
                "sender": {
                    "login": "username",
                    "id": 123456
                }
            }
        }
    )