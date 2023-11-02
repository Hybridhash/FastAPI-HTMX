import pytest
from sqlalchemy import select

from app.database.base import Base
from app.database.db import async_session_maker, engine
from app.models.users import Role


@pytest.fixture(scope="module")
async def db_session():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    session = async_session_maker()
    yield session
    await session.rollback()
    await session.close()


@pytest.fixture(scope="module")
def valid_role():
    return Role(role_name="Ezzeddin", role_desc="Aybak")


class TestRole:
    async def test_author_valid(self, db_session, valid_role):
        async with db_session() as session:
            session.add(valid_role)
            await session.commit()
            aybak = await session.execute(select(Role).filter_by(lastname="Aybak"))
            result = aybak.scalars().first()
            assert result.role_name == "Ezzeddin"
            assert result.desc != "Abdullah"
