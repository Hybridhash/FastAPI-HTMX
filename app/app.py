from fastapi import Depends, FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from loguru import logger

from app.database.db import User, create_db_and_tables
from app.database.security import auth_backend, current_active_user, fastapi_users
from app.exception import http_exception_handler
from app.routes.view.group import group_view_route

# importing the route
from app.routes.view.login import login_view_route
from app.routes.view.role import role_view_route
from app.routes.view.user import user_view_route
from app.schema.users import UserCreate, UserRead, UserUpdate

from fastapi_csrf_protect import CsrfProtect

from app.core.csrf_settings import CsrfSettings

app = FastAPI(exception_handlers={HTTPException: http_exception_handler})
app.mount("/static", StaticFiles(directory="app/static"), name="static")


app.include_router(
    fastapi_users.get_auth_router(auth_backend), prefix="/auth/jwt", tags=["auth"]
)

app.include_router(
    fastapi_users.get_register_router(UserRead, UserCreate),
    prefix="/auth",
    tags=["auth"],
)
app.include_router(
    fastapi_users.get_reset_password_router(),
    prefix="/auth",
    tags=["auth"],
)
app.include_router(
    fastapi_users.get_verify_router(UserRead),
    prefix="/auth",
    tags=["auth"],
)
app.include_router(
    fastapi_users.get_users_router(UserRead, UserUpdate),
    prefix="/users",
    tags=["users"],
)


app.include_router(login_view_route, tags=["Pages", "Authentication/Create"])
app.include_router(role_view_route, tags=["Pages", "Role"])
app.include_router(group_view_route, tags=["Pages", "Group"])
app.include_router(user_view_route, tags=["Pages", "User"])


@app.get("/authenticated-route")
async def authenticated_route(user: User = Depends(current_active_user)):
    logger.info(user.id)
    return {"message": f"Hello {user.email}!"}


@app.on_event("startup")
async def on_startup():
    # Not needed if you setup a migration system like Alembic
    await create_db_and_tables()
    # await create_superuser()
    logger.info("Application started")


@app.on_event("shutdown")
async def on_shutdown():
    logger.info("Application shutdown")


@CsrfProtect.load_config
def get_csrf_config():
    return CsrfSettings()
