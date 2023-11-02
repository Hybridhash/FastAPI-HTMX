import uuid
from datetime import datetime

UUID = uuid.uuid4

# from fastapi import Depends
from sqlalchemy import DateTime
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql.functions import func

from app.database.base import Base


class BaseSQLModel(Base):
    # Abstract defined class that is meant to be subclassed
    __abstract__ = True
    # id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    created: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )
