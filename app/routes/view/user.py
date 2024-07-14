# importing the required modules
import uuid
from datetime import datetime

import nh3
from fastapi import Depends, HTTPException, Request, Response
from fastapi.responses import HTMLResponse
from fastapi.routing import APIRouter

from app.database.db import CurrentAsyncSession
from app.database.security import current_active_user
from app.models.users import Role as RoleModelDB
from app.models.users import User as UserModelDB
from app.models.users import UserProfile as UserProfileModelDB
from app.routes.view.errors import handle_error
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
    Route handler function to get the create user page.

    Args:
        request (Request): The request object.
        current_user (UserModelDB): The current user object obtained from the current_active_user dependency.

    Returns:
        TemplateResponse: The HTML response containing the "partials/add_user.html" template.

    Raises:
        HTTPException: If the current user is not a superuser, with a 403 Forbidden status code.
    """
    try:
        if not current_user.is_superuser:
            raise HTTPException(
                status_code=403, detail="Not authorized to view this page"
            )
        # Access the cookies using the Request object

        token = request.cookies.get("fastapiusersauth")
        users = await user_crud.read_all(db, skip, limit, join_relationships=True)

        return templates.TemplateResponse(
            "pages/user.html",
            {
                "request": request,
                "users": users,
                "token": token,
                "user_type": current_user.is_superuser,
            },
        )
    except Exception as e:
        return handle_error("pages/user.html", {"request": request}, e)


@user_view_route.get("/get_create_users", response_class=HTMLResponse)
async def get_create_users(
    request: Request,
    current_user: UserModelDB = Depends(current_active_user),
):
    """
    Route handler function to render the template for creating a new user.

    Args:
        request (Request): The incoming HTTP request object.
        current_user (UserModelDB): The currently authenticated user object, obtained from the current_active_user dependency.

    Returns:
        TemplateResponse: The rendered HTML template for creating a new user.

    Raises:
        HTTPException: If the current user is not a superuser, with a 403 Forbidden status code and a detail message.
    """
    # checking the current user as super user
    try:
        if not current_user.is_superuser:
            raise HTTPException(status_code=403, detail="Not authorized to add users")
        # Redirecting to the add role page upon successful role creation
        return templates.TemplateResponse(
            "partials/user/add_user.html",
            {"request": request},
        )
    except Exception as e:
        return handle_error("partials/user/add_user.html", {"request": request}, e)


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
    try:
        roles = await role_crud.read_all(db, skip, limit)
        # checking the current user as super user
        if not current_user.is_superuser:
            raise HTTPException(
                status_code=403, detail="Not authorized to view this page"
            )
        user = await user_crud.read_by_primary_key(db, user_id, join_relationships=True)
        return templates.TemplateResponse(
            "partials/user/edit_user.html",
            {
                "request": request,
                "user": user,
                "roles": roles,
            },
        )
    except Exception as e:
        return handle_error(
            "partials/user/edit_user.html",
            {
                "request": request,
                "user": user,
                "roles": roles,
            },
            e,
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

        if role_id is None:
            raise HTTPException(
                status_code=400, detail="Role is required to create a user Profile"
            )

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
    except Exception as e:
        user = await user_crud.read_by_primary_key(db, user_id, join_relationships=True)
        roles = await role_crud.read_all(db)
        return handle_error(
            "partials/user/edit_user.html",
            {
                "request": request,
                "user": user,
                "roles": roles,
            },
            e,
        )
