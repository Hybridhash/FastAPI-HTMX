from typing import Annotated, AsyncGenerator

from fastapi import Depends
from fastapi_users.db import SQLAlchemyUserDatabase
from fastapi_users.password import PasswordHelper
from loguru import logger
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.base import async_session_maker
from app.models.users import User


async def create_db_and_tables():
    # async with engine.begin() as conn:
    #     logger.info("Creating database tables...")
    #     await conn.run_sync(Base.metadata.create_all)

    async with async_session_maker() as session:
        password_helper = PasswordHelper()
        # Statement to check that user is created already for super user email
        select_stmt = select(User).where(User.email == "superuser@admin.com")

        # Query to database to execute the statement
        query = await session.execute(select_stmt)
        user = User(
            email="superuser@admin.com",
            hashed_password=password_helper.hash("password123"),
            is_superuser=True,
            is_active=True,
        )
        if not query.scalars().first():
            logger.info(
                f"Creating superuser... email: {user.email} | password: password123"
            )
            session.add(user)
            await session.commit()
        else:  # pragma: no cover
            logger.info(
                f"Superuser already exists.... email: {user.email} | password: password123"
            )


async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_maker() as session:
        yield session


async def get_user_db(session: AsyncSession = Depends(get_async_session)):
    yield SQLAlchemyUserDatabase(session, User)


CurrentAsyncSession = Annotated[AsyncSession, Depends(get_async_session)]
