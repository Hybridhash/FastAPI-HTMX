from fastapi import Depends, FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from loguru import logger

from app.database.db import User, create_db_and_tables
from app.database.security import auth_backend, current_active_user, fastapi_users
from app.exception import http_exception_handler

# importing the user role route
from app.routes.api.role import role_router
from app.routes.view.login import login_view_route
from app.schema.users import UserCreate, UserRead, UserUpdate

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

# User 
app.include_router(role_router)

app.include_router(login_view_route, tags=["Pages", "Authentication"])

@app.get("/authenticated-route")
async def authenticated_route(user: User = Depends(current_active_user)):
    logger.info(user.id)
    return {"message": f"Hello {user.email}!"}


@app.on_event("startup")
async def on_startup():
    # Not needed if you setup a migration system like Alembic
    await create_db_and_tables()
    # await create_superuser()

# @app.exception_handler(HTTPException)
# async def http_exception_handler(request: Request, exc: HTTPException):
#     if exc.status_code == HTTP_401_UNAUTHORIZED:
#         return RedirectResponse('/login')
#     return exc

# @app.exception_handler(HTTPException)
# async def http_exception_handler(request: Request, exc: HTTPException):
#     if exc and exc.status_code == 401:
#         return RedirectResponse("/login")
#     # elif exc:
#     #     # return await templates.TemplateResponse("error.html", {"request": request, "error": exc})
#     #     pass
#     else:
#         route = request.scope.get("path")
#         method = request.scope.get("method")
#         logger.error(f"Error in route {method} {route}: {exc.detail} : {exc.status_code}")
#         return Response(status_code=200)
    