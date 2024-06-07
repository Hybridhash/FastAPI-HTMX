import json
import uuid

import nh3
from fastapi import Depends, HTTPException, Request, Response
from fastapi.responses import HTMLResponse
from fastapi.routing import APIRouter
from loguru import logger
from pydantic import ValidationError
from sqlalchemy import select

from app.database.db import CurrentAsyncSession
from app.database.security import current_active_user
from app.models.groups import Group as GroupModelDB
from app.models.groups import UserGroupLink as UserGroupLinkModelDB
from app.models.users import User as UserModelDB
from app.models.users import UserProfile as UserProfileModelDB
from app.routes.view.view_crud import SQLAlchemyCRUD
from app.schema.group import GroupCreate
from app.schema.group import GroupUserLink as GroupUserLinkCreate
from app.templates import templates

group_view_route = APIRouter()


group_crud = SQLAlchemyCRUD[GroupModelDB](
    GroupModelDB, related_models={UserModelDB: "users"}
)
user_crud = SQLAlchemyCRUD[UserModelDB](
    UserModelDB,
    related_models={UserProfileModelDB: "profile"},
)


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
        # raise HTTPException(status_code=403, detail="Not authorized to add groups")

        return templates.TemplateResponse(
            "pages/groups.html",
            {
                "request": request,
                "error_message": "You are not authorized to view this page",
            },
        )

    # Access the cookies using the Request object
    groups = await group_crud.read_all(db, skip, limit, join_relationships=True)

    return templates.TemplateResponse(
        "pages/groups.html",
        {
            "request": request,
            "groups": groups,
        },
    )


# Defining a route to get the user profile based on id
@group_view_route.get("/get_user_profile/{user_id}", response_class=HTMLResponse)
async def get_user_profile(
    request: Request,
    user_id: uuid.UUID,
    db: CurrentAsyncSession,
    current_user: UserModelDB = Depends(current_active_user),
):
    if not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="Not authorized to add groups")
    user_profile = await user_crud.read_by_primary_key(
        db, user_id, join_relationships=True
    )
    return templates.TemplateResponse(
        "partials/group/group_user_profile.html",
        {
            "request": request,
            "user_profile": user_profile,
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
        raise HTTPException(status_code=403, detail="Not authorized to add groups")
    # Redirecting to the add group page upon successful group creation
    return templates.TemplateResponse(
        "partials/add_group.html",
        {"request": request},
    )


# Route to get the group by ID
@group_view_route.get("/get_group/{group_id}", response_class=HTMLResponse)
async def get_group_by_id(
    request: Request,
    group_id: uuid.UUID,
    db: CurrentAsyncSession,
    current_user: UserModelDB = Depends(current_active_user),
):
    # checking the current user as super user
    if not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="Not authorized to add groups")
    group = await group_crud.read_by_primary_key(db, group_id)
    return templates.TemplateResponse(
        "partials/edit_group.html",
        {
            "request": request,
            "group": group,
        },
    )


@group_view_route.post("/post_create_group", response_class=HTMLResponse)
async def post_create_group(
    request: Request,
    response: Response,
    db: CurrentAsyncSession,
    current_user: UserModelDB = Depends(current_active_user),
):
    # checking the current user as super user
    if not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="Not authorized to add groups")

    try:
        form = await request.form()

        # Iterate over the form fields and sanitize the values before validating against the Pydantic model
        group_create = GroupCreate(
            group_name=nh3.clean(str(form.get("group_name"))),
            group_desc=nh3.clean(str(form.get("group_desc"))),
        )

        existing_group = await group_crud.read_by_column(
            db, "group_name", group_create.group_name
        )

        if existing_group:
            raise HTTPException(status_code=400, detail="Group name already exists")
        await group_crud.create(dict(group_create), db)

        # Redirecting to the add group page upon successful group creation
        headers = {
            "HX-Location": "/groups",
            "HX-Trigger": json.dumps(
                {
                    "showAlert": {
                        "type": "added",
                        "message": "Group added successfully",
                    }
                }
            ),
        }

        return HTMLResponse(content="", headers=headers)

    except ValidationError as e:
        logger.debug(e.errors())
        return templates.TemplateResponse(
            "partials/add_group.html",
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
            "partials/add_group.html",
            {"request": request, "error_messages": [e.detail]},
        )
    except Exception as e:
        logger.debug(e)
        return templates.TemplateResponse(
            "partials/add_group.html",
            {
                "request": request,
                "error_messages": ["An unexpected error occurred: {}".format(e)],
            },
        )


# Route to update a group
@group_view_route.put("/post_update_group{group_id}", response_class=HTMLResponse)
async def post_update_group(
    request: Request,
    response: Response,
    group_id: uuid.UUID,
    db: CurrentAsyncSession,
    current_user: UserModelDB = Depends(current_active_user),
):
    # checking the current user as super user
    if not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="Not authorized to add groups")

    try:
        form = await request.form()

        # Iterate over the form fields and sanitize the values before validating against the Pydantic model
        group_update = GroupCreate(
            group_name=nh3.clean(str(form.get("group_name"))),
            group_desc=nh3.clean(str(form.get("group_desc"))),
        )

        await group_crud.update(db, group_id, dict(group_update))

        # Redirecting to the add group page upon successful group creation
        headers = {
            "HX-Location": "/groups",
            "HX-Trigger": json.dumps(
                {
                    "showAlert": {
                        "type": "updated",
                        "message": "Group updated successfully",
                    }
                }
            ),
        }
        return HTMLResponse(content="", headers=headers)
    except ValidationError as e:
        logger.debug(e.errors())
        return templates.TemplateResponse(
            "partials/edit_group.html",
            {
                "request": request,
                "group": await group_crud.read_by_primary_key(db, group_id),
                "error_messages": [
                    f"{str(error['loc']).strip('(),')}: {error['msg']}"
                    for error in e.errors()
                ],
            },
        )
    except HTTPException as e:
        return templates.TemplateResponse(
            "partials/edit_group.html",
            {"request": request, "error_messages": [e.detail]},
        )
    except Exception as e:
        return templates.TemplateResponse(
            "partials/edit_group.html",
            {
                "request": request,
                "error_messages": ["An unexpected error occurred: {}".format(e)],
            },
        )


# Route to delete a group
@group_view_route.delete("/delete_group/{group_id}", response_class=HTMLResponse)
async def delete_group(
    request: Request,
    group_id: uuid.UUID,
    db: CurrentAsyncSession,
    current_user: UserModelDB = Depends(current_active_user),
):
    # checking the current user as super user
    if not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="Not authorized to add groups")
    await group_crud.delete(db, group_id)
    headers = {
        "HX-Location": "/groups",
        "HX-Trigger": json.dumps(
            {
                "showAlert": {
                    "type": "deleted",
                    "message": f"Group id: {group_id} deleted successfully",
                }
            }
        ),
    }
    return HTMLResponse(content="", headers=headers)


"""
Group Users Allocation Routes
"""


# Defining a route getting the page for allocating users to the selected group
@group_view_route.get("/get_group_users/{group_id}", response_class=HTMLResponse)
async def get_group_users(
    request: Request,
    group_id: uuid.UUID,
    db: CurrentAsyncSession,
    current_user: UserModelDB = Depends(current_active_user),
):
    # checking the current user as super user
    if not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="Not authorized to add groups")
    group = await group_crud.read_by_primary_key(db, group_id)
    # users = ["user1", "user2", "user3", "user4", "user5"]
    users = await user_crud.read_all(db, join_relationships=True)
    return templates.TemplateResponse(
        "partials/group/add_group_user.html",
        {
            "request": request,
            "group": group,
            "users": users,
        },
    )


# Update the UserGroupLink model based on selected user for a group


@group_view_route.post("/post_group_user_link/{group_id}", response_class=HTMLResponse)
async def post_group_user_link(
    request: Request,
    response: Response,
    group_id: uuid.UUID,
    db: CurrentAsyncSession,
    current_user: UserModelDB = Depends(current_active_user),
):
    # checking the current user as super user
    if not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="Not authorized to add groups")
    try:
        form = await request.form()

        db_data = []
        for user_id in form.getlist("users_selected"):
            group_user_link = GroupUserLinkCreate(
                group_id=uuid.UUID(nh3.clean(str(group_id))),
                user_id=uuid.UUID(nh3.clean(str(user_id))),
            )
            group_id = group_user_link.group_id
            user_id = group_user_link.user_id
            existing_record = await db.scalar(
                select(UserGroupLinkModelDB).filter_by(
                    group_id=group_id, user_id=user_id
                )
            )
            if existing_record:
                print("Record already exists")
            else:
                db_data.append(
                    group_user_link.model_dump(exclude={"id"}, exclude_unset=True)
                )

        if len(db_data) > 0:
            db.add_all([UserGroupLinkModelDB(**link) for link in db_data])
            await db.commit()
        headers = {
            "HX-Location": "/groups",
            "HX-Trigger": json.dumps(
                {
                    "showAlert": {
                        "type": "added",
                        "message": "User allocated successfully",
                    }
                }
            ),
        }

        return HTMLResponse(content="", headers=headers)

    except ValidationError as e:
        logger.debug(e.errors())
        return templates.TemplateResponse(
            "partials/group/add_group_user.html",
            {
                "request": request,
                "group": await group_crud.read_by_primary_key(db, group_id),
                "error_messages": [
                    f"{str(error['loc']).strip('(),')}: {error['msg']}"
                    for error in e.errors()
                ],
            },
        )
    except HTTPException as e:
        return templates.TemplateResponse(
            "partials/group/add_group_user.html",
            {"request": request, "error_messages": [e.detail]},
        )
    except Exception as e:
        return templates.TemplateResponse(
            "partials/group/add_group_user.html",
            {
                "request": request,
                "error_messages": ["An unexpected error occurred: {}".format(e)],
            },
        )
