import nh3
from fastapi import Depends, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.routing import APIRouter
from loguru import logger
from pydantic import ValidationError

from app.database.db import CurrentAsyncSession
from app.database.security import current_active_user
from app.models.groups import Group as GroupModelDB
from app.models.users import User as UserModelDB
from app.routes.view.view_crud import SQLAlchemyCRUD
from app.templates import templates

# Creating a group API route
group_view_route = APIRouter()


group_crud = SQLAlchemyCRUD[GroupModelDB](GroupModelDB)


# Defining a route to navigate to the group page
@group_view_route.get("/groups", response_class=HTMLResponse)
async def get_groups(
    request: Request,
    db: CurrentAsyncSession,
    current_user: UserModelDB = Depends(current_active_user),
    skip: int = 0,
    limit: int = 100,
):
    if not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="Not authorized to add roles")
    # Access the cookies using the Request object
    groups = await group_crud.read_all(db, skip, limit)
    return templates.TemplateResponse(
        "pages/groups.html",
        {
            "request": request,
            "groups": groups,
        },
    )


# Defining a route to add a new group to the database
@group_view_route.get("/get_create_group", response_class=HTMLResponse)
async def get_create_group(
    request: Request,
    current_user: UserModelDB = Depends(current_active_user),
):
    # checking the current user as super user
    if not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="Not authorized to add roles")

    try:
        form = await request.form()

        # Iterate over the form fields and sanitize the values before validating against the Pydantic model
        role_create = RoleCreate(
            role_name=nh3.clean(str(form.get("role_name"))),
            role_desc=nh3.clean(str(form.get("role_desc"))),
        )

        existing_role = await role_crud.read_by_column(
            db, "role_name", role_create.role_name
        )
        logger.debug(existing_role)
        if existing_role:
            raise HTTPException(status_code=400, detail="Role name already exists")
        await role_crud.create(dict(role_create), db)

        # Redirecting to the add role page upon successful role creation
        headers = {
            "HX-Location": "/role",
            "HX-Trigger": "roleAdded",
        }

        return HTMLResponse(content="", headers=headers)

    except ValidationError as e:
        logger.debug(e.errors())
        return templates.TemplateResponse(
            "partials/add_role.html",
            {
                "request": request,
                "error_messages": [
                    f"{str(error['loc']).strip('(),')}: {error['msg']}"
                    for error in e.errors()
                ],
            },
        )
    except HTTPException as e:
        return templates.TemplateResponse(
            "partials/add_role.html",
            {"request": request, "error_messages": [e.detail]},
        )
    except Exception as e:
        logger.debug(e)
        return templates.TemplateResponse(
            "partials/add_role.html",
            {
                "request": request,
                "error_messages": ["An unexpected error occurred: {}".format(e)],
            },
        )
