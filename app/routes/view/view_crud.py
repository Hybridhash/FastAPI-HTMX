import uuid
from typing import Any, Dict, Generic, List, Optional, Type, TypeVar

from fastapi import HTTPException
from sqlalchemy import func, select
from sqlalchemy.orm import joinedload

from app.database.base import Base
from app.database.db import CurrentAsyncSession

ModelType = TypeVar("ModelType", bound=Base)


class SQLAlchemyCRUD(Generic[ModelType]):
    """
    A generic class for performing common database operations using SQLAlchemy.

    Args:
        db_model (Type[ModelType]): The SQLAlchemy model class to be used for database operations.
        related_models (Optional[Dict[Type[Base], str]]): A dictionary of related SQLAlchemy model classes and the relationship
            attribute name to be used for JOIN queries.
    """

    def __init__(
        self,
        db_model: Type[ModelType],
        related_models: Optional[Dict[Type[Base], str]] = None,
    ):
        self.db_model = db_model
        self.related_models = related_models if related_models is not None else {}

    async def create(self, data: dict[str, Any], db: CurrentAsyncSession) -> ModelType:
        """
        Creates a new record in the database.

        Args:
            data (dict[str, Any]): The data to be inserted into the database record.
            db (CurrentAsyncSession): The database session to be used for the operation.

        Returns:
            ModelType: The newly created database record.
        """
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
        """
        Retrieves all records from the database, optionally with pagination.

        Args:
            db (CurrentAsyncSession): The database session to be used for the operation.
            skip (int, optional): The number of records to skip. Defaults to 0.
            limit (int, optional): The maximum number of records to return. Defaults to 0 (no limit).
            join_relationships (bool, optional): Whether to JOIN related tables. Defaults to False.

        Returns:
            List[ModelType]: A list of database records.
        """
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
        """
        Retrieves a single record from the database by its primary key.

        Args:
            db (CurrentAsyncSession): The database session to be used for the operation.
            id (uuid.UUID): The primary key of the record to be retrieved.
            join_relationships (bool, optional): Whether to JOIN related tables. Defaults to False.

        Returns:
            ModelType: The retrieved database record.

        Raises:
            HTTPException: If the record cannot be found.
        """
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
        """
        Retrieves a single record from the database by a column other than the primary key.

        Args:
            db (CurrentAsyncSession): The database session to be used for the operation.
            column_name (str): The name of the column to be used for the search.
            column_value (Any): The value of the column to be used for the search.

        Returns:
            ModelType | None: The retrieved database record, or None if no record was found.
        """
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
        """
        Updates a single record in the database by its primary key.

        Args:
            db (CurrentAsyncSession): The database session to be used for the operation.
            id (uuid.UUID): The primary key of the record to be updated.
            data (dict[str, Any]): The data to be updated in the record.

        Returns:
            ModelType | None: The updated database record, or None if the record could not be found.
        """
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
        """
        Deletes a single record from the database by its primary key.

        Args:
            db (CurrentAsyncSession): The database session to be used for the operation.
            id (uuid.UUID): The primary key of the record to be deleted.

        Returns:
            bool: True if the record was deleted, False if the record could not be found.
        """
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
