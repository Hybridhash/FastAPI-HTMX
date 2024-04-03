# importing the required modules
import uuid

# import nh3
from fastapi import Depends, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.routing import APIRouter
from loguru import logger

from app.database.db import CurrentAsyncSession
from app.database.security import current_active_user
from app.models.users import Role as RoleModelDB
from app.models.users import User as UserModelDB
from app.models.users import UserProfile as UserProfileModelDB
from app.routes.view.view_crud import SQLAlchemyCRUD

# from app.schema.users import RoleCreate
from app.templates import templates

# Create an APIRouter
user_view_route = APIRouter()


user_crud = SQLAlchemyCRUD[UserModelDB](
    UserModelDB, related_models={RoleModelDB: "role", UserProfileModelDB: "profile"}
)


"""
This function is used to get the list of all users.

:param request: The request object
:param db: The database session
:param skip: The number of records to skip
:param limit: The maximum number of records to return
:return: The list of users
"""


@user_view_route.get("/user", response_class=HTMLResponse)
async def get_users(
    request: Request,
    db: CurrentAsyncSession,
    skip: int = 0,
    limit: int = 100,
):
    # Access the cookies using the Request object
    users = await user_crud.read_all(db, skip, limit, join_relationships=True)
    logger.info(f"users: {users}")
    return templates.TemplateResponse(
        "pages/user.html",
        {
            "request": request,
            "users": users,
        },
    )


"""
This function is used to get the create user page.

:param request: The request object
:param current_user: The current user
:return: The create roles page
"""


@user_view_route.get("/get_create_users", response_class=HTMLResponse)
async def get_create_users(
    request: Request,
    current_user: UserModelDB = Depends(current_active_user),
):
    # checking the current user as super user
    if not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="Not authorized to add users")
    # Redirecting to the add role page upon successful role creation
    return templates.TemplateResponse(
        "partials/add_user.html",
        {"request": request},
    )


# # Defining a post view route for adding a new role to the database
# @user_view_route.post("/post_create_roles", response_class=HTMLResponse)
# async def post_create_roles(
#     request: Request,
#     response: Response,
#     db: CurrentAsyncSession,
#     current_user: UserModelDB = Depends(current_active_user),
# ):
#     # checking the current user as super user
#     if not current_user.is_superuser:
#         raise HTTPException(status_code=403, detail="Not authorized to add roles")

#     try:
#         form = await request.form()

#         # Iterate over the form fields and sanitize the values before validating against the Pydantic model
#         role_create = RoleCreate(
#             role_name=nh3.clean(str(form.get("role_name"))),
#             role_desc=nh3.clean(str(form.get("role_desc"))),
#         )

#         existing_role = await role_crud.read_by_column(
#             db, "role_name", role_create.role_name
#         )
#         logger.debug(existing_role)
#         if existing_role:
#             raise HTTPException(status_code=400, detail="Role name already exists")
#         await role_crud.create(dict(role_create), db)

#         # Redirecting to the add role page upon successful role creation
#         headers = {
#             "HX-Location": "/role",
#             "HX-Trigger": "roleAdded",
#         }

#         return HTMLResponse(content="", headers=headers)

#     except ValidationError as e:
#         logger.debug(e.errors())
#         return templates.TemplateResponse(
#             "partials/add_role.html",
#             {
#                 "request": request,
#                 "error_messages": [
#                     f"{str(error['loc']).strip('(),')}: {error['msg']}"
#                     for error in e.errors()
#                 ],
#             },
#         )
#     except HTTPException as e:
#         return templates.TemplateResponse(
#             "partials/add_role.html",
#             {"request": request, "error_messages": [e.detail]},
#         )
#     except Exception as e:
#         logger.debug(e)
#         return templates.TemplateResponse(
#             "partials/add_role.html",
#             {
#                 "request": request,
#                 "error_messages": ["An unexpected error occurred: {}".format(e)],
#             },
#         )


# Defining end point to get the record based on the id
@user_view_route.get("/get_user/{user_id}", response_class=HTMLResponse)
async def get_user_by_id(
    request: Request,
    user_id: uuid.UUID,
    db: CurrentAsyncSession,
    current_user: UserModelDB = Depends(current_active_user),
):
    # checking the current user as super user
    if not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="Not authorized to add roles")
    role = await user_crud.read_by_primary_key(db, user_id)
    return templates.TemplateResponse(
        "partials/edit_user.html",
        {
            "request": request,
            "role": role,
        },
    )


# # Defining end point to update the record based on the id
# @user_view_route.put("/post_update_role/{role_id}", response_class=HTMLResponse)
# async def post_update_role(
#     request: Request,
#     response: Response,
#     role_id: uuid.UUID,
#     db: CurrentAsyncSession,
#     current_user: UserModelDB = Depends(current_active_user),
# ):
#     # checking the current user as super user
#     if not current_user.is_superuser:
#         raise HTTPException(status_code=403, detail="Not authorized to add roles")

#     try:
#         form = await request.form()

#         # Iterate over the form fields and sanitize the values before validating against the Pydantic model
#         role_update = RoleCreate(
#             role_name=nh3.clean(str(form.get("role_name"))),
#             role_desc=nh3.clean(str(form.get("role_desc"))),
#         )

#         await role_crud.update(db, role_id, dict(role_update))

#         # Redirecting to the add role page upon successful role creation
#         headers = {
#             "HX-Location": "/role",
#             "HX-Trigger": "roleUpdated",
#         }
#         return HTMLResponse(content="", headers=headers)
#     except ValidationError as e:
#         logger.debug(e.errors())
#         return templates.TemplateResponse(
#             "partials/edit_role.html",
#             {
#                 "request": request,
#                 "role": await role_crud.read_by_primary_key(db, role_id),
#                 "error_messages": [
#                     f"{str(error['loc']).strip('(),')}: {error['msg']}"
#                     for error in e.errors()
#                 ],
#             },
#         )
#     except HTTPException as e:
#         return templates.TemplateResponse(
#             "partials/edit_role.html",
#             {"request": request, "error_messages": [e.detail]},
#         )
#     except Exception as e:
#         return templates.TemplateResponse(
#             "partials/edit_role.html",
#             {
#                 "request": request,
#                 "error_messages": ["An unexpected error occurred: {}".format(e)],
#             },
#         )


# # Defining a route to delete the record based on the id
# @user_view_route.delete("/delete_role/{role_id}", response_class=HTMLResponse)
# async def delete_role(
#     request: Request,
#     role_id: uuid.UUID,
#     db: CurrentAsyncSession,
#     current_user: UserModelDB = Depends(current_active_user),
# ):
#     # checking the current user as super user
#     if not current_user.is_superuser:
#         raise HTTPException(status_code=403, detail="Not authorized to add roles")
#     await role_crud.delete(db, role_id)
#     headers = {
#         "HX-Location": "/role",
#         "HX-Trigger": "roleDeleted",
#     }
#     return HTMLResponse(content="", headers=headers)
