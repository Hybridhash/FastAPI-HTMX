from datetime import datetime

from fastapi_users.db import SQLAlchemyBaseUserTableUUID

# from fastapi_users_db_sqlalchemy import GUID
from sqlalchemy import UUID, DateTime, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql.functions import func
from sqlalchemy.sql.schema import ForeignKey

from app.models.base import Base, BaseSQLModel
from app.models.groups import Group
from app.models.upload import Upload


class User(SQLAlchemyBaseUserTableUUID, Base):
    __tablename__ = "users"
    created: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )
    # add 1 to 1 relationship with the role model keeping default as None
    # Default value on creating user is None and updated later
    role_id: Mapped[UUID] = mapped_column(
        ForeignKey("roles.id"), nullable=True, default=None
    )
    # Role is defined in quotes to avoid type errors
    role: Mapped["Role"] = relationship(
        "Role",
        uselist=False,
        back_populates="user",
    )
    profile_id: Mapped[UUID] = mapped_column(
        ForeignKey("user_profiles.id"), nullable=True, default=None
    )
    # Profile 1 to 1 relationship with the user model
    profile: Mapped["UserProfile"] = relationship(
        "UserProfile",
        uselist=False,
        back_populates="user",
        cascade="all, delete",
    )
    # items: Mapped["Item"] = relationship(back_populates="user", cascade="all, delete")
    # Creating a relationship with the activity model
    activity: Mapped["UserActivity"] = relationship(
        "UserActivity", back_populates="user"
    )
    uploads: Mapped["Upload"] = relationship(
        "Upload",
        back_populates="user",
        cascade="all, delete",
    )
    # Creating a relationship with the group user link model
    groups: Mapped["Group"] = relationship(
        "Group",
        secondary="group_users",
        back_populates="users",
        uselist=True,
    )

    # string representation of an object
    def __repr__(self):
        return f"User(id={self.id!r}, name={self.email!r})"


class UserProfile(BaseSQLModel):
    """
    Model to hold the profile of a user

    Parameters:
        first_name (str): The first name of the user.
        last_name (str): The last name of the user.
        gender (str, optional): The gender of the user.
        date_of_birth (datetime, optional): The date of birth of the user.
        city (str, optional): The city of the user.
        country (str, optional): The country of the user.
        address (str, optional): The address of the user.
        phone (str, optional): The phone number of the user.
        company (str, optional): The company of the user.
    """

    __tablename__ = "user_profiles"
    first_name: Mapped[str] = mapped_column(String(length=120), index=True)
    last_name: Mapped[str] = mapped_column(String(length=120), index=True)
    gender: Mapped[str | None] = mapped_column(String(length=10), nullable=True)
    date_of_birth: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    city: Mapped[str | None] = mapped_column(String(length=50), nullable=True)
    country: Mapped[str | None] = mapped_column(String(length=50), nullable=True)
    address: Mapped[str | None] = mapped_column(String(length=255), nullable=True)
    phone: Mapped[str | None] = mapped_column(String(length=20), nullable=True)
    company: Mapped[str | None] = mapped_column(String(length=100), nullable=True)
    user: Mapped["User"] = relationship("User", back_populates="profile")


class Role(BaseSQLModel):
    """
    A Role represents a set of permissions and privileges granted to a user.

    Parameters:
        role_name (str): The name of the role, e.g., "admin", "moderator", etc.
        role_desc (str, optional): A description of the role.
    """

    __tablename__ = "roles"
    role_name: Mapped[str] = mapped_column(
        String(length=200), nullable=False, unique=True
    )
    role_desc: Mapped[str | None] = mapped_column(String(length=1024), nullable=True)

    # user_id: Mapped[UUID] = mapped_column(GUID, ForeignKey("users.id"))
    user: Mapped["User"] = relationship("User", back_populates="role")


class UserActivity(BaseSQLModel):
    """
    Tracks user activities such as sign-ins, sign-ups, and other events.

    Parameters:
        user_id (UUID): The ID of the user.
        activity_date (datetime): The date and time of the activity.
        activity_type (str): The type of activity, such as "sign-in" or "sign-up".
        activity_desc (str): A description of the activity.
    """

    __tablename__ = "user_activity"
    user_id: Mapped[UUID] = mapped_column(ForeignKey("users.id"), default=None)
    activity_date: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=func.now()
    )
    activity_type: Mapped[str] = mapped_column(String(length=200), nullable=False)
    activity_desc: Mapped[str | None] = mapped_column(
        String(length=1024), nullable=True
    )
    user: Mapped["User"] = relationship("User", back_populates="activity")
    user: Mapped["User"] = relationship("User", back_populates="activity")
