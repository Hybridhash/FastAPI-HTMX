import uuid
from typing import Any, Dict, Generic, List, Optional, Type, TypeVar

from fastapi import HTTPException
from sqlalchemy import func, select
from sqlalchemy.orm import joinedload

from app.database.base import Base
from app.database.db import CurrentAsyncSession

ModelType = TypeVar("ModelType", bound=Base)


class SQLAlchemyCRUD(Generic[ModelType]):
    def __init__(
        self,
        db_model: Type[ModelType],
        related_models: Optional[Dict[Type[Base], str]] = None,
    ):
        self.db_model = db_model
        self.related_models = related_models if related_models is not None else {}

    async def create(self, data: dict[str, Any], db: CurrentAsyncSession) -> ModelType:
        """Creates a new record in the database."""
        new_record = self.db_model(**data)
        db.add(new_record)
        await db.commit()
        return new_record

    async def read_all(
        self,
        db: CurrentAsyncSession,
        skip: int = 0,
        limit: int = 0,
        join_relationships: bool = False,
    ) -> List[ModelType]:
        """Retrieves all records from the database, optionally with pagination."""
        stmt = select(self.db_model)
        if join_relationships:
            for related_model, join_column in self.related_models.items():
                relationship = getattr(self.db_model, join_column, None)
                print(relationship)
                if relationship is not None:
                    stmt = stmt.options(joinedload(relationship))
                else:
                    # Handle error or invalid relationship specification
                    raise ValueError(f"No relationship found for {join_column}")
        stmt = stmt.offset(skip)
        if limit:
            stmt = stmt.limit(limit)
        query = await db.execute(stmt)
        return list(query.scalars().all())

    async def read_by_primary_key(
        self,
        db: CurrentAsyncSession,
        id: uuid.UUID,
        join_relationships: bool = False,
    ) -> ModelType:
        """Retrieves a single record from the database by its primary key."""
        stmt = select(self.db_model)
        if join_relationships:
            for related_model, join_column in self.related_models.items():
                relationship = getattr(self.db_model, join_column, None)
                print(relationship)
                if relationship is not None:
                    stmt = stmt.options(joinedload(relationship))
                else:
                    # Handle error or invalid relationship specification
                    raise ValueError(f"No relationship found for {join_column}")
        stmt = stmt.where(self.db_model.id == id)
        query = await db.execute(stmt)
        record = query.scalar()
        if not record:
            raise HTTPException(status_code=404, detail=f"Record with {id} not found")
        return record

    async def read_by_column(
        self, db: CurrentAsyncSession, column_name: str, column_value: Any
    ) -> ModelType | None:
        """Retrieves a single record from the database by a column other than the primary key."""
        if isinstance(column_value, str):
            column_value = column_value.lower()
        stmt = select(self.db_model).where(
            func.lower(getattr(self.db_model, column_name)) == column_value
        )
        query = await db.execute(stmt)
        record = query.scalar()
        return record

    async def update(
        self, db: CurrentAsyncSession, id: uuid.UUID, data: dict[str, Any]
    ) -> ModelType | None:
        """Updates a single record in the database by its primary key."""
        stmt = select(self.db_model).where(self.db_model.id == id)
        query = await db.execute(stmt)
        if not query:
            raise HTTPException(status_code=404, detail=f"Record with {id} not found")
        db_item = query.scalar_one()
        if db_item:
            for key, value in data.items():
                setattr(db_item, key, value)
            await db.commit()
            await db.refresh(db_item)
            return db_item

    async def delete(
        self,
        db: CurrentAsyncSession,
        id: uuid.UUID,
    ) -> bool:
        """Deletes a single record from the database by its primary key."""
        stmt = select(self.db_model).where(self.db_model.id == id)
        query = await db.execute(stmt)
        if not query:
            raise HTTPException(status_code=404, detail=f"Record with {id} not found")
        db_item = query.scalar_one()
        if db_item:
            await db.delete(db_item)
            await db.commit()
            return True
        return False
