import uuid
from typing import Generic, Type, TypeVar

from fastapi import HTTPException
from pydantic import BaseModel
from sqlalchemy import select

# from sqlalchemy.orm import Session
from app.database.base import Base
from app.database.db import CurrentAsyncSession

ModelType = TypeVar("ModelType", bound=Base)
PydanticCreateModelType = TypeVar("PydanticCreateModelType", bound=BaseModel)
PydanticUpdateModelType = TypeVar("PydanticUpdateModelType", bound=BaseModel)
IdentifierType = TypeVar("IdentifierType")

class BaseCRUD(Generic[ModelType, PydanticCreateModelType, PydanticUpdateModelType]):
    def __init__(self, db_model: Type[ModelType], 
                 pydantic_create_model: Type[PydanticCreateModelType], 
                 pydantic_update_model: Type[PydanticUpdateModelType]):
        self.db_model = db_model
        self.pydantic_create_model = pydantic_create_model
        self.pydantic_update_model = pydantic_update_model

    async def create(self,  item: PydanticCreateModelType, 
                     db: CurrentAsyncSession,) -> ModelType:
        db_item = self.db_model(**item.dict())
        db.add(db_item)
        await db.commit()
        await db.refresh(db_item)
        return db_item
    
    async def read_all(self, db: CurrentAsyncSession, skip: int, limit: int):
        # Querying the database model using SQLAlchemy select()
        stmt = select(self.db_model).offset(skip).limit(limit)
        query = await db.execute(stmt)
        # Adding a exception to be raised in case if record not exists
        if not query:
            raise HTTPException(status_code=404, detail="Record not found")
        return query.scalars().all()
    
        # return db.query(self.db_model).offset(skip).limit(limit).all()

    # Reading the one record only from the database model
    async def read(self, db: CurrentAsyncSession, id: uuid.UUID) -> ModelType | None:
        stmt = select(self.db_model).where(self.db_model.id == id)
        query = await db.execute(stmt)
        if not query:
            raise HTTPException(status_code=404, detail=f"Record with {id} not found")
        return query.scalar_one_or_none()
    
    # Adding a database operation function to update the record
    async def update(self, db: CurrentAsyncSession, id: uuid.UUID, 
                    item: PydanticUpdateModelType) -> ModelType | None:
        stmt = select(self.db_model).where(self.db_model.id == id)
        query = await db.execute(stmt)
        if not query:
             raise HTTPException(status_code=404, detail=f"Record with {id} not found")
        db_item = query.scalar_one()
        if db_item:
            for key, value in item.dict().items():
                setattr(db_item, key, value)
            await db.commit()
            await db.refresh(db_item)
            return db_item

    # Adding a database model to delete a record
    async def delete(self,db:CurrentAsyncSession, id: uuid.UUID, ):
        stmt = select(self.db_model).where(self.db_model.id == id)
        query = await db.execute(stmt)
        if not query:
            raise HTTPException(status_code=404, detail=f"Record with {id} not found")
        db_item = query.scalar_one()
        if db_item:
            await db.delete(db_item)
            await db.commit()
            return db_item

    # def delete(self, db: Session, id: int):
    #     db_item = db.query(self.db_model).filter(self.db_model.id == id).first()
    #     if db_item:
    #         db.delete(db_item)
    #         db.commit()
    #         return db_item
    #     else:
    #         raise HTTPException(status_code=404, detail="Item not found")


    # async def create(self, data: Dict[str, Any]) -> Any:
    #     obj = self.model(**data)
    #     self.db_session.add(obj)
    #     self.db_session.commit()
    #     self.db_session.refresh(obj)
    #     return obj

    # def read(self, id: int) -> Any:
    #     return self.db_session.query(self.model).filter(self.model.id == id).first()

    # def update(self, id: int, data: Dict[str, Any]) -> Any:
    #     obj = self.db_session.query(self.model).filter(self.model.id == id).first()
    #     for key, value in data.items():
    #         setattr(obj, key, value)
    #     self.db_session.commit()
    #     self.db_session.refresh(obj)
    #     return obj

    # def delete(self, id: int) -> Any:
    #     obj = self.db_session.query(self.model).filter(self.model.id == id).first()
    #     self.db_session.delete(obj)
    #     self.db_session.commit()



# @app.post("/create/{model_name}")
# def create(model_name: str, data: Dict[str, Any], db: Session = Depends(get_db)):
#     model = globals()[model_name]
#     crud = BaseCRUD(model, db)
#     return crud.create(data)

# @app.get("/read/{model_name}/{id}")
# def read(model_name: str, id: int, db: Session = Depends(get_db)):
#     model = globals()[model_name]
#     crud = BaseCRUD(model, db)
#     return crud.read(id)

# @app.put("/update/{model_name}/{id}")
# def update(model_name: str, id: int, data: Dict[str, Any], db: Session = Depends(get_db)):
#     model = globals()[model_name]
#     crud = BaseCRUD(model, db)
#     return crud.update(id, data)

# @app.delete("/delete/{model_name}/{id}")
# def delete(model_name: str, id: int, db: Session = Depends(get_db)):
#     model = globals()[model_name]
#     crud = BaseCRUD(model, db)
#     return crud.delete(id)