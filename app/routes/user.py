from fastapi import Depends
from fastapi.exceptions import HTTPException
from fastapi.routing import APIRouter

from app.database.db import CurrentAsyncSession
from app.database.security import current_active_user
from app.models.users import Role as RoleModelDB
from app.models.users import User as UserModelDB
from app.routes.crud import BaseCRUD
from app.schema.users import RoleCreate

role_crud = BaseCRUD(RoleModelDB, RoleCreate)

# Creating a router for roles
role_router = APIRouter(prefix="/roles", tags=["Roles"])

# Creating a route for roles inside the user route
# @router.get('/roles', response_model=RoleCreate)
# async def get_roles():
#     pass


# Creating a route for posting new roles inside the user route
# @role_router.post('', response_model=RoleCreate)
# async def create_roles(role: RoleCreate, db: CurrentAsyncSession, 
#                        current_user: UserModelDB = Depends(current_active_user)):
#     # checking the current user as super user
#     if not current_user.is_superuser:
#         raise HTTPException(status_code=400, detail="Not Authorized to create roles")
#     db_role = RoleModelDB (**role.dict())
#     db.add(db_role)
#     await db.commit()
#     await db.refresh(db_role)
#     return db_role


@role_router.post('', response_model=RoleCreate)
async def create_roles(role: RoleCreate, db: CurrentAsyncSession, 
                       current_user: UserModelDB = Depends(current_active_user)):
    # checking the current user as super user
    if not current_user.is_superuser:
        raise HTTPException(status_code=400, detail="Not Authorized to create roles")
    db_role = await role_crud.create(role, db)
    return db_role