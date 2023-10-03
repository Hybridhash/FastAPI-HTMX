from datetime import datetime

# from fastapi import Depends
from fastapi_users.db import SQLAlchemyBaseUserTableUUID
from fastapi_users_db_sqlalchemy import GUID
from sqlalchemy import UUID, DateTime, String

# from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql.functions import func
from sqlalchemy.sql.schema import ForeignKey

from app.models.base import Base, BaseSQLModel


class User(SQLAlchemyBaseUserTableUUID, Base):
    __tablename__ = "users"
    created: Mapped[datetime] = mapped_column(DateTime(timezone=True), 
                                              server_default=func.now())
    updated: Mapped[datetime] = mapped_column(DateTime(timezone=True), 
                                              server_default=func.now(),
                                              onupdate=func.now()
    )
    # add 1 to 1 relationship with the role class
    # Role is defined in quotes to avoid type errors
    roles: Mapped["Role"] = relationship("Role", uselist=False, back_populates="users")
    # items: Mapped["Item"] = relationship(back_populates="user", cascade="all, delete")

    # string representation of an object
    def __repr__(self):
        return f"User(id={self.id!r}, name={self.email!r})"
    
class Role (BaseSQLModel):
    __tablename__ = "roles"
    role_name: Mapped[str] = mapped_column(String(length=200), nullable=False)
    role_name: Mapped[str] = mapped_column(String(length=1024), nullable=False)
    user_id: Mapped[UUID] = mapped_column(GUID, ForeignKey("users.id"))
    user: Mapped["User"] = relationship("User", back_populates="roles")