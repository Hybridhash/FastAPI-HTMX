# importing the required modules
import uuid
from datetime import datetime

import nh3

# import nh3
from fastapi import Depends, HTTPException, Request, Response
from fastapi.responses import HTMLResponse
from fastapi.routing import APIRouter
from loguru import logger
from pydantic import ValidationError

from app.database.db import CurrentAsyncSession
from app.database.security import current_active_user
from app.models.users import Role as RoleModelDB
from app.models.users import User as UserModelDB
from app.models.users import UserProfile as UserProfileModelDB
from app.routes.view.view_crud import SQLAlchemyCRUD
from app.schema.users import ProfileUpdate

# from app.schema.users import RoleCreate
from app.templates import templates

# Create an APIRouter
user_view_route = APIRouter()


user_crud = SQLAlchemyCRUD[UserModelDB](
    UserModelDB, related_models={RoleModelDB: "role", UserProfileModelDB: "profile"}
)
user_profile_crud = SQLAlchemyCRUD[UserProfileModelDB](UserProfileModelDB)

role_crud = SQLAlchemyCRUD[RoleModelDB](RoleModelDB)


@user_view_route.get("/user", response_class=HTMLResponse)
async def get_users(
    request: Request,
    db: CurrentAsyncSession,
    skip: int = 0,
    limit: int = 100,
    current_user: UserModelDB = Depends(current_active_user),
):
    """
    This function is used to get the create user page.

    Args:
        request (Request): The request object.
        current_user (UserModelDB): The current user object obtained from the current_active_user dependency.

    Returns:
        TemplateResponse: The HTML response containing the "partials/add_user.html" template.

    Raises:
        HTTPException: If the current user is not a superuser, with a 403 Forbidden status code.
    """
    if not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="Not authorized to add users")
    # Access the cookies using the Request object
    users = await user_crud.read_all(db, skip, limit, join_relationships=True)

    return templates.TemplateResponse(
        "pages/user.html",
        {
            "request": request,
            "users": users,
        },
    )


@user_view_route.get("/get_create_users", response_class=HTMLResponse)
async def get_create_users(
    request: Request,
    current_user: UserModelDB = Depends(current_active_user),
):
    """
    Used to get the create user page.

    :param request: The request object
    :param current_user: The current user
    :return: The create roles page

    """
    # checking the current user as super user
    if not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="Not authorized to add users")
    # Redirecting to the add role page upon successful role creation
    return templates.TemplateResponse(
        "partials/add_user.html",
        {"request": request},
    )


# Defining end point to get the record based on the id
@user_view_route.get("/get_user/{user_id}", response_class=HTMLResponse)
async def get_user_by_id(
    request: Request,
    user_id: uuid.UUID,
    db: CurrentAsyncSession,
    current_user: UserModelDB = Depends(current_active_user),
    skip: int = 0,
    limit: int = 100,
):
    roles = await role_crud.read_all(db, skip, limit)
    # checking the current user as super user
    if not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="Not authorized to add roles")
    user = await user_crud.read_by_primary_key(db, user_id, join_relationships=True)
    logger.debug(user)
    return templates.TemplateResponse(
        "partials/user/edit_user.html",
        {
            "request": request,
            "user": user,
            "roles": roles,
        },
    )


# Defining a endpoint to update the record based on the id
@user_view_route.put("/post_update_user/{user_id}", response_class=HTMLResponse)
async def post_update_user(
    request: Request,
    response: Response,
    user_id: uuid.UUID,
    db: CurrentAsyncSession,
    current_user: UserModelDB = Depends(current_active_user),
):
    logger.debug(current_user)
    # checking the current user as super user
    if not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="Not authorized to add users")
    try:
        form = await request.form()
        # Iterate over the form fields and sanitize the values before validating against the Pydantic model
        profile_data = ProfileUpdate(
            first_name=nh3.clean(str(form.get("first_name"))),
            last_name=nh3.clean(str(form.get("last_name"))),
            gender=nh3.clean(str(form.get("gender"))),
            date_of_birth=(
                datetime.strptime(nh3.clean(str(form.get("dob"))), "%Y-%m-%d")
                if form.get("dob")
                else None
            ),
            address=nh3.clean(str(form.get("address"))),
            city=nh3.clean(str(form.get("city"))),
            country=nh3.clean(str(form.get("country"))),
            phone=nh3.clean(str(form.get("phone"))),
            company=nh3.clean(str(form.get("company"))),
        )

        role_id = (nh3.clean(str(form.get("role_id"))),)
        role_id = uuid.UUID(role_id[0]) if role_id[0] else None

        # Fetch the user being updated
        user_to_update = await user_crud.read_by_primary_key(db, user_id)

        if user_to_update.profile_id is None:

            # Create UserProfile
            new_profile = await user_profile_crud.create(dict(profile_data), db)

            # Update user profile id
            await user_crud.update(db, user_id, {"profile_id": new_profile.id})

            # Update user role
            if role_id:
                await user_crud.update(db, user_id, {"role_id": role_id})

            headers = {
                "HX-Location": "/user",
                "HX-Trigger": "roleUpdated",
            }
            return HTMLResponse(content="", headers=headers)
        else:
            # Update existing user profile
            await user_profile_crud.update(
                db, user_to_update.profile_id, dict(profile_data)
            )

            # Update user role
            if role_id:
                await user_crud.update(db, user_id, {"role_id": role_id})

            headers = {
                "HX-Location": "/user",
                "HX-Trigger": "roleUpdated",
            }
            return HTMLResponse(content="", headers=headers)

    except ValidationError as e:
        logger.debug(e.errors())
        return templates.TemplateResponse(
            "partials/user/edit_user.html",
            {
                "request": request,
                "user": await user_crud.read_by_primary_key(
                    db, user_id, join_relationships=True
                ),
                "error_messages": [
                    f"{str(error['loc']).strip('(),')}: {error['msg']}"
                    for error in e.errors()
                ],
            },
        )
    except HTTPException as e:
        return templates.TemplateResponse(
            "partials/user/edit_user.html",
            {
                "request": request,
                "error_messages": [e.detail],
                "user": await user_crud.read_by_primary_key(
                    db, user_id, join_relationships=True
                ),
            },
        )
    except Exception as e:
        return templates.TemplateResponse(
            "partials/user/edit_user.html",
            {
                "request": request,
                "user": await user_crud.read_by_primary_key(
                    db, user_id, join_relationships=True
                ),
                "error_messages": ["An unexpected error occurred: {}".format(e)],
            },
        )


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
#     return HTMLResponse(content="", headers=headers)
