import uuid

from fastapi import Depends
from fastapi.exceptions import HTTPException
from fastapi.routing import APIRouter

from app.database.db import CurrentAsyncSession
from app.database.security import current_active_user
from app.models.users import Role as RoleModelDB
from app.models.users import User as UserModelDB
from app.routes.api.crud import BaseCRUD
from app.schema.users import RoleBase, RoleCreate, RoleRead, RoleUpdate

role_crud = BaseCRUD[RoleModelDB, RoleCreate, RoleUpdate](
    RoleModelDB, RoleCreate, RoleUpdate
)

# Creating a router for roles
role_router = APIRouter(prefix="/roles", tags=["Roles"])


# Endpoint for creating roles
@role_router.post("/", response_model=RoleCreate)
async def create_roles(
    role: RoleCreate,
    db: CurrentAsyncSession,
    current_user: UserModelDB = Depends(current_active_user),
):
    # checking the current user as super user
    if not current_user.is_superuser:
        raise HTTPException(status_code=400, detail="Not Authorized to create roles")
    db_role = await role_crud.create(role, db)
    return db_role


# End point for reading all available roles
@role_router.get("/", response_model=list[RoleBase])
async def read_role_all(
    db: CurrentAsyncSession,
    skip: int = 0,
    limit: int = 100,
    current_user: UserModelDB = Depends(current_active_user),
):
    # checking the current user as super user
    if not current_user.is_superuser:
        raise HTTPException(status_code=400, detail="Not Authorized to create roles")
    return await role_crud.read_all(db, skip, limit)


# Endpoint for reading a role based on UUID
@role_router.get("/{role_id}", response_model=RoleRead)
async def read_role_by_id(
    role_id: uuid.UUID,
    db: CurrentAsyncSession,
    current_user: UserModelDB = Depends(current_active_user),
):
    # checking the current user as super user
    if not current_user.is_superuser:
        raise HTTPException(status_code=400, detail="Not Authorized to create roles")
    return await role_crud.read(db, role_id)


# Endpoint for updating a role based on UUID
@role_router.put("/{role_id}", response_model=RoleUpdate)
async def update_role_by_id(
    role_id: uuid.UUID,
    role: RoleUpdate,
    db: CurrentAsyncSession,
    current_user: UserModelDB = Depends(current_active_user),
):
    # checking the current user as super user
    if not current_user.is_superuser:
        raise HTTPException(status_code=400, detail="Not Authorized to create roles")
    return await role_crud.update(db, role_id, role)


# Endpoint for deleting a role based on UUID
@role_router.delete("/{role_id}", response_model=RoleBase)
async def delete_role_by_id(
    role_id: uuid.UUID,
    db: CurrentAsyncSession,
    current_user: UserModelDB = Depends(current_active_user),
):
    # checking the current user as super user
    if not current_user.is_superuser:
        raise HTTPException(status_code=400, detail="Not Authorized to create roles")
    return await role_crud.delete(db, role_id)
