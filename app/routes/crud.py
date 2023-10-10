from typing import Generic, Type, TypeVar

from pydantic import BaseModel
from sqlalchemy import select

# from sqlalchemy.orm import Session
from app.database.base import Base
from app.database.db import CurrentAsyncSession

ModelType = TypeVar("ModelType", bound=Base)
PydanticModelType = TypeVar("PydanticModelType", bound=BaseModel)

class BaseCRUD(Generic[ModelType, PydanticModelType]):
    def __init__(self, db_model: Type[ModelType], pydantic_model: Type[PydanticModelType]):
        self.db_model = db_model
        self.pydantic_model = pydantic_model

    async def create(self,  item: PydanticModelType, db: CurrentAsyncSession,) -> ModelType:
        db_item = self.db_model(**item.dict())
        db.add(db_item)
        await db.commit()
        await db.refresh(db_item)
        return db_item
    
    async def read_all(self, db: CurrentAsyncSession, skip: int, limit: int):
        # Querying the database model using SQLAlchemy select()
        stmt = select(self.db_model).offset(skip).limit(limit)
        query = await db.execute(stmt)
        return query.scalars().all()
    
        # return db.query(self.db_model).offset(skip).limit(limit).all()


    # def read(self, db: Session, id: int):
    #     return db.query(self.db_model).filter(self.db_model.id == id).first()

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