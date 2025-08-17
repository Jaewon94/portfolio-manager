"""
GitHub 저장소 관련 API 엔드포인트
프로젝트와 연결된 GitHub 저장소 CRUD 및 동기화 기능
"""

from typing import Any, Dict, List, Optional

from app.core.database import get_db
from app.core.exceptions import ExternalAPIException
from app.models.user import User
from app.schemas.github import (
    GithubCommit,
    GithubRepository,
    GithubRepositoryCreate,
    GithubRepositoryStats,
    GithubRepositorySync,
    GithubRepositoryUpdate,
    GithubWebhookPayload,
)
from app.services.auth import get_current_user
from app.services.github import GithubRepositoryService
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter()


@router.get("/", response_model=List[GithubRepository])
async def list_github_repositories(
    project_id: Optional[int] = Query(None, description="프로젝트 ID로 필터링"),
    sync_enabled: Optional[bool] = Query(
        None, description="동기화 활성화 상태로 필터링"
    ),
    limit: int = Query(10, ge=1, le=100, description="결과 수 제한"),
    offset: int = Query(0, ge=0, description="결과 오프셋"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """GitHub 저장소 목록 조회"""
    service = GithubRepositoryService(db)
    repositories = await service.list_repositories(
        owner_id=current_user.id,
        project_id=project_id,
        sync_enabled=sync_enabled,
        limit=limit,
        offset=offset,
    )
    return repositories


@router.post("/", response_model=GithubRepository, status_code=status.HTTP_201_CREATED)
async def create_github_repository(
    repository_data: GithubRepositoryCreate,
    project_id: int = Query(..., description="연결할 프로젝트 ID"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """GitHub 저장소 연결"""
    service = GithubRepositoryService(db)

    # 프로젝트 소유권 확인
    from app.services.project import ProjectService

    project_service = ProjectService(db)
    project = await project_service.get_project_by_id(project_id)

    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="프로젝트를 찾을 수 없습니다"
        )

    if project.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="해당 프로젝트에 대한 권한이 없습니다",
        )

    repository = await service.create_github_repository(
        project_id=project_id, data=repository_data
    )
    return repository


@router.get("/{repository_id}", response_model=GithubRepository)
async def get_github_repository(
    repository_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """GitHub 저장소 상세 조회"""
    service = GithubRepositoryService(db)
    repository = await service.get_repository_by_id(repository_id)

    if not repository:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="GitHub 저장소를 찾을 수 없습니다",
        )

    # 소유권 확인
    from app.services.project import ProjectService

    project_service = ProjectService(db)
    project = await project_service.get_project_by_id(repository.project_id)

    if project and project.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="해당 저장소에 대한 권한이 없습니다",
        )

    return repository


@router.put("/{repository_id}", response_model=GithubRepository)
async def update_github_repository(
    repository_id: int,
    repository_data: GithubRepositoryUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """GitHub 저장소 정보 수정"""
    service = GithubRepositoryService(db)
    repository = await service.get_repository_by_id(repository_id)

    if not repository:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="GitHub 저장소를 찾을 수 없습니다",
        )

    # 소유권 확인
    from app.services.project import ProjectService

    project_service = ProjectService(db)
    project = await project_service.get_project_by_id(repository.project_id)

    if project and project.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="해당 저장소에 대한 권한이 없습니다",
        )

    updated_repository = await service.update_repository(
        repository_id=repository_id, repository_data=repository_data
    )
    return updated_repository


@router.delete("/{repository_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_github_repository(
    repository_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """GitHub 저장소 삭제"""
    service = GithubRepositoryService(db)
    repository = await service.get_repository_by_id(repository_id)

    if not repository:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="GitHub 저장소를 찾을 수 없습니다",
        )

    # 소유권 확인
    from app.services.project import ProjectService

    project_service = ProjectService(db)
    project = await project_service.get_project_by_id(repository.project_id)

    if project and project.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="해당 저장소에 대한 권한이 없습니다",
        )

    success = await service.delete_repository(repository_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="GitHub 저장소를 찾을 수 없습니다",
        )


@router.post("/{repository_id}/sync", response_model=GithubRepository)
async def sync_github_repository(
    repository_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """GitHub 저장소 동기화"""
    service = GithubRepositoryService(db)
    repository = await service.get_repository_by_id(repository_id)

    if not repository:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="GitHub 저장소를 찾을 수 없습니다",
        )

    # 소유권 확인
    from app.services.project import ProjectService

    project_service = ProjectService(db)
    project = await project_service.get_project_by_id(repository.project_id)

    if project and project.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="해당 저장소에 대한 권한이 없습니다",
        )

    try:
        synced_repository = await service.sync_repository_by_id(repository_id)
        return synced_repository
    except ExternalAPIException as e:
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=str(e))


@router.get("/{repository_id}/commits", response_model=List[GithubCommit])
async def get_commit_history(
    repository_id: int,
    limit: int = Query(100, ge=1, le=100, description="조회할 커밋 수"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """GitHub 저장소 커밋 히스토리 조회"""
    service = GithubRepositoryService(db)
    repository = await service.get_repository_by_id(repository_id)

    if not repository:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="GitHub 저장소를 찾을 수 없습니다",
        )

    # 소유권 확인
    from app.services.project import ProjectService

    project_service = ProjectService(db)
    project = await project_service.get_project_by_id(repository.project_id)

    if project and project.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="해당 저장소에 대한 권한이 없습니다",
        )

    try:
        commits = await service.get_commit_history(repository_id, limit)
        return commits
    except ExternalAPIException as e:
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=str(e))


@router.post("/bulk-sync", response_model=Dict[str, Any])
async def bulk_sync_repositories(
    repository_ids: List[int],
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """여러 GitHub 저장소 일괄 동기화"""
    service = GithubRepositoryService(db)

    # 모든 저장소의 소유권 확인
    for repo_id in repository_ids:
        repository = await service.get_repository_by_id(repo_id)
        if repository:
            from app.services.project import ProjectService

            project_service = ProjectService(db)
            project = await project_service.get_project_by_id(repository.project_id)

            if project and project.owner_id != current_user.id:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"저장소 {repo_id}에 대한 권한이 없습니다",
                )

    results = await service.bulk_sync_repositories(repository_ids)
    return results


async def get_github_repository(
    repository_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """GitHub 저장소 상세 조회"""
    service = GithubRepositoryService(db)
    repository = await service.get_repository_by_id(repository_id)

    if not repository:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="GitHub 저장소를 찾을 수 없습니다",
        )

    # 소유권 확인
    from app.services.project import ProjectService

    project_service = ProjectService(db)
    project = await project_service.get_project_by_id(repository.project_id)

    if project and project.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="해당 저장소에 대한 권한이 없습니다",
        )

    return repository


@router.put("/{repository_id}", response_model=GithubRepository)
async def update_github_repository(
    repository_id: int,
    repository_data: GithubRepositoryUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """GitHub 저장소 정보 수정"""
    service = GitHubRepositoryService(db)
    repository = await service.get_repository_by_id(repository_id)

    if not repository:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="GitHub 저장소를 찾을 수 없습니다",
        )

    # 소유권 확인
    from app.services.project import ProjectService

    project_service = ProjectService(db)
    project = await project_service.get_project_by_id(repository.project_id)

    if project and project.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="해당 저장소에 대한 권한이 없습니다",
        )

    updated_repository = await service.update_repository(
        repository_id=repository_id, repository_data=repository_data
    )
    return updated_repository


@router.delete("/{repository_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_github_repository(
    repository_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """GitHub 저장소 연결 해제"""
    service = GitHubRepositoryService(db)
    repository = await service.get_repository_by_id(repository_id)

    if not repository:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="GitHub 저장소를 찾을 수 없습니다",
        )

    # 소유권 확인
    from app.services.project import ProjectService

    project_service = ProjectService(db)
    project = await project_service.get_project_by_id(repository.project_id)

    if project and project.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="해당 저장소에 대한 권한이 없습니다",
        )

    await service.delete_repository(repository_id)


@router.post("/{repository_id}/sync", response_model=GithubRepositorySync)
async def sync_github_repository(
    repository_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """GitHub 저장소 정보 동기화"""
    service = GitHubRepositoryService(db)
    repository = await service.get_repository_by_id(repository_id)

    if not repository:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="GitHub 저장소를 찾을 수 없습니다",
        )

    # 소유권 확인
    from app.services.project import ProjectService

    project_service = ProjectService(db)
    project = await project_service.get_project_by_id(repository.project_id)

    if project and project.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="해당 저장소에 대한 권한이 없습니다",
        )

    sync_result = await service.sync_repository(repository_id)
    return sync_result


@router.get("/{repository_id}/commits", response_model=List[GithubCommit])
async def get_repository_commits(
    repository_id: int,
    limit: int = Query(10, ge=1, le=100, description="결과 수 제한"),
    page: int = Query(1, ge=1, description="페이지 번호"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """GitHub 저장소 커밋 목록 조회"""
    service = GitHubRepositoryService(db)
    repository = await service.get_repository_by_id(repository_id)

    if not repository:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="GitHub 저장소를 찾을 수 없습니다",
        )

    # 소유권 확인
    from app.services.project import ProjectService

    project_service = ProjectService(db)
    project = await project_service.get_project_by_id(repository.project_id)

    if project and project.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="해당 저장소에 대한 권한이 없습니다",
        )

    commits = await service.get_repository_commits(
        repository_id=repository_id, limit=limit, page=page
    )
    return commits


@router.get("/{repository_id}/stats", response_model=GithubRepositoryStats)
async def get_repository_stats(
    repository_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """GitHub 저장소 통계 조회"""
    service = GitHubRepositoryService(db)
    repository = await service.get_repository_by_id(repository_id)

    if not repository:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="GitHub 저장소를 찾을 수 없습니다",
        )

    # 소유권 확인
    from app.services.project import ProjectService

    project_service = ProjectService(db)
    project = await project_service.get_project_by_id(repository.project_id)

    if project and project.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="해당 저장소에 대한 권한이 없습니다",
        )

    stats = await service.get_repository_stats(repository_id)
    return stats


@router.post("/webhook", status_code=status.HTTP_200_OK)
async def github_webhook(
    payload: GithubWebhookPayload, db: AsyncSession = Depends(get_db)
):
    """GitHub Webhook 처리"""
    service = GitHubRepositoryService(db)
    await service.handle_webhook(payload)
    return {"message": "Webhook processed successfully"}


# 프로젝트별 GitHub 저장소 조회
@router.get("/project/{project_id}", response_model=List[GithubRepository])
async def get_project_repositories(
    project_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """특정 프로젝트의 GitHub 저장소 목록 조회"""
    # 프로젝트 소유권 확인
    from app.services.project import ProjectService

    project_service = ProjectService(db)
    project = await project_service.get_project_by_id(project_id)

    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="프로젝트를 찾을 수 없습니다"
        )

    if project.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="해당 프로젝트에 대한 권한이 없습니다",
        )

    service = GithubRepositoryService(db)
    repositories = await service.list_repositories(
        owner_id=current_user.id, project_id=project_id
    )
    return repositories


# 프로젝트별 GitHub 저장소 조회 (기존 URL 구조 지원)
@router.get("/projects/{project_id}/github", response_model=Dict[str, Any])
async def get_project_github_repository(
    project_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """특정 프로젝트의 GitHub 저장소 조회 (기존 URL 구조 지원)"""
    # 프로젝트 소유권 확인
    from app.services.project import ProjectService

    project_service = ProjectService(db)
    project = await project_service.get_project_by_id(project_id)

    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="프로젝트를 찾을 수 없습니다"
        )

    if project.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="해당 프로젝트에 대한 권한이 없습니다",
        )

    service = GithubRepositoryService(db)
    repository = await service.get_by_project_id(project_id)

    if not repository:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="GitHub repository not found",
        )

    return {
        "success": True,
        "data": {
            "id": repository.id,
            "project_id": repository.project_id,
            "github_url": repository.github_url,
            "repository_name": repository.repository_name,
            "stars": repository.stars,
            "forks": repository.forks,
            "watchers": repository.watchers,
            "language": repository.language,
            "license": repository.license,
            "sync_enabled": repository.sync_enabled,
            "is_private": repository.is_private,
            "is_fork": repository.is_fork,
            "last_synced_at": repository.last_synced_at,
            "sync_error_message": repository.sync_error_message,
            "created_at": repository.created_at,
            "updated_at": repository.updated_at,
        },
    }


# 프로젝트별 GitHub 저장소 업데이트 (기존 URL 구조 지원)
@router.patch("/projects/{project_id}/github", response_model=Dict[str, Any])
async def update_project_github_repository(
    project_id: int,
    repository_data: GithubRepositoryUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """특정 프로젝트의 GitHub 저장소 업데이트 (기존 URL 구조 지원)"""
    # 프로젝트 소유권 확인
    from app.services.project import ProjectService

    project_service = ProjectService(db)
    project = await project_service.get_project_by_id(project_id)

    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="프로젝트를 찾을 수 없습니다"
        )

    if project.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="해당 프로젝트에 대한 권한이 없습니다",
        )

    service = GithubRepositoryService(db)
    repository = await service.get_by_project_id(project_id)

    if not repository:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="GitHub repository not found",
        )

    updated_repository = await service.update_repository(
        repository_id=repository.id, repository_data=repository_data
    )

    return {
        "success": True,
        "data": {
            "id": updated_repository.id,
            "project_id": updated_repository.project_id,
            "github_url": updated_repository.github_url,
            "repository_name": updated_repository.repository_name,
            "stars": updated_repository.stars,
            "forks": updated_repository.forks,
            "watchers": updated_repository.watchers,
            "language": updated_repository.language,
            "license": updated_repository.license,
            "sync_enabled": updated_repository.sync_enabled,
            "is_private": updated_repository.is_private,
            "is_fork": updated_repository.is_fork,
            "last_synced_at": updated_repository.last_synced_at,
            "sync_error_message": updated_repository.sync_error_message,
            "created_at": updated_repository.created_at,
            "updated_at": updated_repository.updated_at,
        },
    }


# 프로젝트별 GitHub 저장소 삭제 (기존 URL 구조 지원)
@router.delete("/projects/{project_id}/github", status_code=status.HTTP_204_NO_CONTENT)
async def delete_project_github_repository(
    project_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """특정 프로젝트의 GitHub 저장소 삭제 (기존 URL 구조 지원)"""
    # 프로젝트 소유권 확인
    from app.services.project import ProjectService

    project_service = ProjectService(db)
    project = await project_service.get_project_by_id(project_id)

    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="프로젝트를 찾을 수 없습니다"
        )

    if project.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="해당 프로젝트에 대한 권한이 없습니다",
        )

    service = GithubRepositoryService(db)
    repository = await service.get_by_project_id(project_id)

    if not repository:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="GitHub repository not found",
        )

    success = await service.delete_repository(repository.id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="GitHub repository not found",
        )


# 프로젝트별 GitHub 저장소 동기화 (기존 URL 구조 지원)
@router.post("/projects/{project_id}/github/sync", response_model=Dict[str, Any])
async def sync_project_github_repository(
    project_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """특정 프로젝트의 GitHub 저장소 동기화 (기존 URL 구조 지원)"""
    # 프로젝트 소유권 확인
    from app.services.project import ProjectService

    project_service = ProjectService(db)
    project = await project_service.get_project_by_id(project_id)

    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="프로젝트를 찾을 수 없습니다"
        )

    if project.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="해당 프로젝트에 대한 권한이 없습니다",
        )

    service = GithubRepositoryService(db)
    repository = await service.get_by_project_id(project_id)

    if not repository:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="GitHub repository not found",
        )

    try:
        synced_repository = await service.sync_repository(repository.id)
        return {
            "success": True,
            "data": {
                "id": synced_repository.id,
                "project_id": synced_repository.project_id,
                "github_url": synced_repository.github_url,
                "repository_name": synced_repository.repository_name,
                "stars": synced_repository.stars,
                "forks": synced_repository.forks,
                "watchers": synced_repository.watchers,
                "language": synced_repository.language,
                "license": synced_repository.license,
                "sync_enabled": synced_repository.sync_enabled,
                "is_private": synced_repository.is_private,
                "is_fork": synced_repository.is_fork,
                "last_synced_at": synced_repository.last_synced_at,
                "sync_error_message": synced_repository.sync_error_message,
                "created_at": synced_repository.created_at,
                "updated_at": synced_repository.updated_at,
            },
        }
    except ExternalAPIException as e:
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=str(e))


# 프로젝트별 GitHub 저장소 커밋 히스토리 (기존 URL 구조 지원)
@router.get("/projects/{project_id}/github/commits", response_model=Dict[str, Any])
async def get_project_commit_history(
    project_id: int,
    limit: int = Query(100, ge=1, le=100, description="조회할 커밋 수"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """특정 프로젝트의 GitHub 저장소 커밋 히스토리 (기존 URL 구조 지원)"""
    # 프로젝트 소유권 확인
    from app.services.project import ProjectService

    project_service = ProjectService(db)
    project = await project_service.get_project_by_id(project_id)

    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="프로젝트를 찾을 수 없습니다"
        )

    if project.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="해당 프로젝트에 대한 권한이 없습니다",
        )

    service = GithubRepositoryService(db)
    repository = await service.get_by_project_id(project_id)

    if not repository:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="GitHub repository not found",
        )

    try:
        commits = await service.get_commit_history(repository.id, limit)
        return {"success": True, "data": commits}
    except ExternalAPIException as e:
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=str(e))
