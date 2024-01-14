# from fastapi import Depends

from sqlalchemy import UUID, Enum, String

# from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql.schema import ForeignKey

from app.models.base import BaseSQLModel

# from app.models.users import User


class Permission(Enum):
    READ = "read"
    WRITE = "write"
    DELETE = "delete"
    ADMIN = "admin"


class Group(BaseSQLModel):
    __tablename__ = "group"
    group_name: Mapped[str] = mapped_column(
        String(length=200), nullable=False, unique=True
    )
    group_desc: Mapped[str | None] = mapped_column(String(length=1024), nullable=True)

    # Creating enum for the permission to be given to the group
    permission: Mapped[Permission] = mapped_column(Permission, nullable=True)

    group_users: Mapped["UserGroupLink"] = relationship(
        "UserGroupLink", back_populates="group"
    )


class UserGroupLink(BaseSQLModel):
    __tablename__ = "group_users"
    group_id: Mapped[UUID] = mapped_column(ForeignKey("group.id"), default=None)
    user_id: Mapped[UUID] = mapped_column(ForeignKey("users.id"))

    group: Mapped[Group] = relationship(Group, back_populates="group_users")
    user: Mapped["User"] = relationship("User", back_populates="group_users")
