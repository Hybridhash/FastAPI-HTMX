from datetime import datetime

# from fastapi import Depends
from fastapi_users.db import SQLAlchemyBaseUserTableUUID
from sqlalchemy import DateTime

# from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy.sql.functions import func

# from app.database.db import get_async_session


# Declarating the base class for all models
class Base(DeclarativeBase):
    pass

# # Creating a base user using the SQLAlchemyBaseUserTableUUID class from FASTAPI-USERS
# class User(SQLAlchemyBaseUserTableUUID, Base):
#     __tablename__ = "users"
#     created: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
#     updated: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
#     # items: Mapped["Item"] = relationship(back_populates="user", cascade="all, delete")

#     # string representation of an object
#     def __repr__(self):
#         return f"User(id={self.id!r}, name={self.email!r})"

# async def get_user_db(session: AsyncSession = Depends(get_async_session)):
#     yield SQLAlchemyUserDatabase(session, User)



class User(SQLAlchemyBaseUserTableUUID, Base):
    __tablename__ = "users"
    created: Mapped[datetime] = mapped_column(DateTime(timezone=True), 
                                              server_default=func.now())
    updated: Mapped[datetime] = mapped_column(DateTime(timezone=True), 
                                              server_default=func.now(),
                                              onupdate=func.now()
    )
    # items: Mapped["Item"] = relationship(back_populates="user", cascade="all, delete")

    # string representation of an object
    def __repr__(self):
        return f"User(id={self.id!r}, name={self.email!r})"