from sqlalchemy import String, Text, ForeignKey, Integer, Boolean, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .base import Base, TimestampMixin
from typing import Optional, TYPE_CHECKING
from datetime import datetime

if TYPE_CHECKING:
    from .project import Project


class GithubRepository(Base, TimestampMixin):
    """
    GitHub 저장소 정보 모델 (3NF 준수를 위해 Project에서 분리)
    CLAUDE.md 명세: (id, project_id, github_url, repository_name, stars, forks, language, license, last_commit_date, sync_enabled)
    """

    __tablename__ = "github_repositories"

    id: Mapped[int] = mapped_column(primary_key=True)
    project_id: Mapped[int] = mapped_column(
        ForeignKey("projects.id"), nullable=False, unique=True  # 1:1 관계 보장
    )
    
    # GitHub 저장소 기본 정보
    github_url: Mapped[str] = mapped_column(String(500), unique=True, nullable=False)
    repository_name: Mapped[str] = mapped_column(String(255), nullable=False)  # owner/repo 형식
    
    # 저장소 통계
    stars: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    forks: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    watchers: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    
    # 저장소 메타데이터
    language: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)  # 주 언어
    license: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)  # 라이선스
    is_private: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    is_fork: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    
    # 최근 커밋 정보
    last_commit_sha: Mapped[Optional[str]] = mapped_column(String(40), nullable=True)
    last_commit_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    last_commit_date: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    
    # 동기화 정보
    last_synced_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True, default=datetime.utcnow
    )
    sync_error_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    sync_enabled: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    # 관계 설정 (1:1)
    project: Mapped["Project"] = relationship("Project", back_populates="github_repository")

    def __repr__(self):
        return f"<GithubRepository(id={self.id}, repo={self.repository_name}, stars={self.stars})>"

    @property
    def owner_name(self) -> Optional[str]:
        """저장소 소유자명 추출 (owner/repo -> owner)"""
        if "/" in self.repository_name:
            return self.repository_name.split("/")[0]
        return None

    @property
    def repo_name(self) -> Optional[str]:
        """저장소명 추출 (owner/repo -> repo)"""
        if "/" in self.repository_name:
            return self.repository_name.split("/")[1]
        return self.repository_name