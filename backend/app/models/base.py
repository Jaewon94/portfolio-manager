from datetime import datetime
from sqlalchemy import DateTime, func
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Mapped, mapped_column

Base = declarative_base()


class TimestampMixin:
    """생성/수정 시간을 자동으로 관리하는 Mixin"""

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )
