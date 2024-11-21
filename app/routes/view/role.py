# importing the required modules
import json
import uuid

import nh3
from fastapi import Depends, HTTPException, Request, Response
from fastapi.responses import HTMLResponse
from fastapi.routing import APIRouter
from fastapi_csrf_protect import CsrfProtect

from app.database.db import CurrentAsyncSession
from app.database.security import current_active_user
from app.models.users import Role as RoleModelDB
from app.models.users import User as UserModelDB
from app.routes.view.errors import handle_error
from app.routes.view.view_crud import SQLAlchemyCRUD
from app.schema.users import RoleCreate
from app.templates import templates

role_view_route = APIRouter()


role_crud = SQLAlchemyCRUD[RoleModelDB](RoleModelDB)


# Defining a view route to navigate to the role page
@role_view_route.get("/role", response_class=HTMLResponse)
async def get_role(
    request: Request,
    db: CurrentAsyncSession,
    current_user: UserModelDB = Depends(current_active_user),
    skip: int = 0,
    limit: int = 100,
    csrf_protect: CsrfProtect = Depends(),
):
    try:
        if not current_user.is_superuser:
            raise HTTPException(
                status_code=403, detail="Not authorized to view this page"
            )
        # Access the cookies using the Request object
        roles = await role_crud.read_all(db, skip, limit)
        csrf_token, signed_token = csrf_protect.generate_csrf_tokens()
        response = templates.TemplateResponse(
            "pages/role.html",
            {
                "request": request,
                "roles": roles,
                "user_type": current_user.is_superuser,
                "csrf_token": csrf_token,
            },
        )
        csrf_protect.set_csrf_cookie(signed_token, response)
        return response
    except Exception as e:
        csrf_token = request.headers.get("X-CSRF-Token")
        return handle_error(
            "pages/role.html", {"request": request, "csrf_token": csrf_token}, e
        )


# Defining a get view route for showing form to add a new role to the database
@role_view_route.get("/get_create_roles", response_class=HTMLResponse)
async def get_create_roles(
    request: Request,
    current_user: UserModelDB = Depends(current_active_user),
    csrf_protect: CsrfProtect = Depends(),
):
    # checking the current user as super user
    try:
        if not current_user.is_superuser:
            raise HTTPException(status_code=403, detail="Not authorized to add roles")
        # Redirecting to the add role page upon successful role creation

        csrf_token = request.headers.get("X-CSRF-Token")
        response = templates.TemplateResponse(
            "partials/role/add_role.html",
            {
                "request": request,
                "csrf_token": csrf_token,
                "user_type": current_user.is_superuser,
            },
        )

        return response
    except Exception as e:
        csrf_token = request.headers.get("X-CSRF-Token")
        return handle_error(
            "partials/role/add_role.html",
            {
                "request": request,
                "csrf_token": csrf_token,
                "user_type": current_user.is_superuser,
            },
            e,
        )


# Defining a post view route for adding a new role to the database
@role_view_route.post("/post_create_roles", response_class=HTMLResponse)
async def post_create_roles(
    request: Request,
    response: Response,
    db: CurrentAsyncSession,
    current_user: UserModelDB = Depends(current_active_user),
    csrf_protect: CsrfProtect = Depends(),
):
    try:

        await csrf_protect.validate_csrf(request)
        # checking the current user as super user
        if not current_user.is_superuser:
            raise HTTPException(status_code=403, detail="Not authorized to add roles")

        form = await request.form()

        # Iterate over the form fields and sanitize the values before validating against the Pydantic model
        role_create = RoleCreate(
            role_name=nh3.clean(str(form.get("role_name"))),
            role_desc=nh3.clean(str(form.get("role_desc"))),
        )

        existing_role = await role_crud.read_by_column(
            db, "role_name", role_create.role_name
        )

        if existing_role:
            raise HTTPException(status_code=400, detail="Role name already exists")
        await role_crud.create(dict(role_create), db)

        csrf_token, signed_token = csrf_protect.generate_csrf_tokens()

        # Redirecting to the add role page upon successful role creation
        headers = {
            "HX-Location": "/role",
            "HX-Trigger": json.dumps(
                {
                    "showAlert": {
                        "type": "added",
                        "message": f"{role_create.role_name} added successfully",
                        "source": "role-page",
                    },
                }
            ),
            "HX-Push-Url": "true",
            "csrf_token": csrf_token,
        }

        response = HTMLResponse(content="", headers=headers)

        csrf_protect.unset_csrf_cookie(response)

        csrf_protect.set_csrf_cookie(signed_token, response)

        return response
    except Exception as e:
        csrf_token = request.headers.get("X-CSRF-Token")
        return handle_error(
            "partials/role/add_role.html",
            {
                "request": request,
                "csrf_token": csrf_token,
                "user_type": current_user.is_superuser,
            },
            e,
        )


# Defining end point to get the record based on the id
@role_view_route.get("/get_role/{role_id}", response_class=HTMLResponse)
async def get_role_by_id(
    request: Request,
    role_id: uuid.UUID,
    db: CurrentAsyncSession,
    current_user: UserModelDB = Depends(current_active_user),
    csrf_protect: CsrfProtect = Depends(),
):
    try:
        # checking the current user as super user
        if not current_user.is_superuser:
            raise HTTPException(status_code=403, detail="Not authorized to add roles")
        role = await role_crud.read_by_primary_key(db, role_id)

        csrf_token = request.headers.get("X-CSRF-Token")

        response = templates.TemplateResponse(
            "partials/role/edit_role.html",
            {
                "request": request,
                "role": role,
                "csrf_token": csrf_token,
                "user_type": current_user.is_superuser,
            },
        )

        return response
    except Exception as e:
        csrf_token = request.headers.get("X-CSRF-Token")
        return handle_error(
            "partials/role/edit_role.html",
            {
                "request": request,
                "csrf_token": csrf_token,
                "user_type": current_user.is_superuser,
            },
            e,
        )


# Defining end point to update the record based on the id
@role_view_route.put("/post_update_role/{role_id}", response_class=HTMLResponse)
async def post_update_role(
    request: Request,
    response: Response,
    role_id: uuid.UUID,
    db: CurrentAsyncSession,
    current_user: UserModelDB = Depends(current_active_user),
    csrf_protect: CsrfProtect = Depends(),
):
    try:
        await csrf_protect.validate_csrf(request)
        # checking the current user as super user
        if not current_user.is_superuser:
            raise HTTPException(status_code=403, detail="Not authorized to add roles")

        form = await request.form()

        # Iterate over the form fields and sanitize the values before validating against the Pydantic model
        role_update = RoleCreate(
            role_name=nh3.clean(str(form.get("role_name"))),
            role_desc=nh3.clean(str(form.get("role_desc"))),
        )

        await role_crud.update(db, role_id, dict(role_update))

        csrf_token, signed_token = csrf_protect.generate_csrf_tokens()
        # Redirecting to the add role page upon successful role creation
        headers = {
            "HX-Location": "/role",
            "HX-Trigger": json.dumps(
                {
                    "showAlert": {
                        "type": "updated",
                        "message": f"{role_update.role_name} updated successfully",
                        "source": "role-page",
                    },
                }
            ),
            "HX-Boost": "true",
            "csrf_token": csrf_token,
        }
        response = HTMLResponse(content="", headers=headers)

        csrf_protect.unset_csrf_cookie(response)

        csrf_protect.set_csrf_cookie(signed_token, response)

        return response
    except Exception as e:
        role = await role_crud.read_by_primary_key(db, role_id)
        csrf_token = request.headers.get("X-CSRF-Token")
        return handle_error(
            "partials/role/edit_role.html",
            {"request": request, "role": role, "csrf_token": csrf_token},
            e,
        )


# Defining a route to delete the record based on the id
@role_view_route.delete("/delete_role/{role_id}", response_class=HTMLResponse)
async def delete_role(
    request: Request,
    role_id: uuid.UUID,
    db: CurrentAsyncSession,
    current_user: UserModelDB = Depends(current_active_user),
    csrf_protect: CsrfProtect = Depends(),
):
    try:
        # checking the current user as super user
        if not current_user.is_superuser:
            raise HTTPException(
                status_code=403, detail="Not authorized to delete roles"
            )
        await role_crud.delete(db, role_id)

        csrf_token, signed_token = csrf_protect.generate_csrf_tokens()
        role_name = request.headers.get("X-Role-Name")
        headers = {
            "HX-Location": "/role",
            "HX-Trigger": json.dumps(
                {
                    "showAlert": {
                        "type": "deleted",
                        "message": f"{role_name} deleted successfully",
                        "source": "role-page",
                    },
                }
            ),
            "HX-Boost": "true",
            "csrf_token": csrf_token,
        }

        response = HTMLResponse(content="", headers=headers)

        csrf_protect.unset_csrf_cookie(response)

        csrf_protect.set_csrf_cookie(signed_token, response)

        return response
    except Exception as e:
        csrf_token = request.headers.get("X-CSRF-Token")
        return handle_error(
            "pages/role.html", {"request": request, "csrf_token": csrf_token}, e
        )
