
import http
from typing import Optional

from fastapi import Depends, Request
from fastapi.responses import HTMLResponse, RedirectResponse, Response
from fastapi.routing import APIRouter
from loguru import logger

from app.database.security import current_active_user, verify_jwt
from app.models.users import User as UserModelDB
from app.routes.view.http import get_login_http
from app.templates import templates

# Create an APIRouter
login_view_route = APIRouter()


# Defining a route to navigate to the dashboard page using the current_active_user dependency
@login_view_route.get("/dashboard", response_class=HTMLResponse)
async def get_dashboard(request: Request, user: UserModelDB = Depends(current_active_user)):
      # Access the cookies using the Request object
    cookies = request.cookies
    cookie_value = cookies.get('fastapiusersauth')
    return templates.TemplateResponse(
        "pages/dashboard.html",
        {"request": request, "title": "My Web Page", "message": f"Welcome to my web page!{user.email}", "cookie_value": cookie_value},
    )


@login_view_route.get("/")
async def get_index(request:Request):
        logger.debug(request.cookies)
        cookies = request.cookies
        cookie_value = cookies.get('fastapiusersauth')
        logger.debug(cookie_value)
        if cookie_value is not None:
            if await verify_jwt(cookie_value):
                return RedirectResponse('/dashboard', status_code=302)
            else:
                return RedirectResponse('/login', status_code=302)
        else:
                return RedirectResponse('/login', status_code=302)

@login_view_route.get("/login",summary="Gets the login page", 
                      tags=["Pages", "Authentication"], response_class=HTMLResponse)
async def get_login(request: Request, invalid: Optional[bool] = None, logged_out: Optional[bool] = None, unauthorized: Optional[bool] = None):
      # Access the cookies using the Request object
    context = {'request': request, 'invalid': invalid, 'logged_out': logged_out, 'unauthorized': unauthorized}
    return templates.TemplateResponse(
        "pages/login.html",
        context
    )

# Defining a route for the login post request
@login_view_route.post("/login", summary="Logs in a user", tags=["Pages","Authentication"])
async def post_login(request: Request, response:Response) -> RedirectResponse:
    logger.info(request)
    form = await request.form()
    username = form.get("username")
    password = form.get("password")
    logger.debug(username)
    logger.debug(password)
    response = RedirectResponse("/", status_code=302)
    await set_cookie(str(form.get("username")), str(form.get("password")),response)
    return response

        
async def set_cookie(username:str, password:str, response:Response) -> None:
    # logger.info(request)
    # form = await request.form()
    # username = form.get("username")
    # password = form.get("password")
    # logger.debug(username)
    # logger.debug(password)

    response.set_cookie("fastapiusersauth", "test", max_age=3600)
    httpx_response = await get_login_http(username, password)
    if httpx_response is not None:
        cookie = http.cookies.SimpleCookie(httpx_response.headers["set-cookie"])["fastapiusersauth"]
        logger.debug(cookie)
        cookie_value = cookie.value
        logger.debug(cookie_value)
        cookie_httponly = cookie["httponly"]
        logger.debug(cookie_httponly)
        cookie_max_age = cookie["max-age"]
        logger.debug(cookie_max_age)
        cookie_path = cookie["path"]
        logger.debug(cookie_path)
        cookie_samesite = cookie["samesite"]
        logger.debug(cookie_samesite)
        
        response.set_cookie(
        key="fastapiusersauth",
        value=cookie_value,
        httponly=cookie_httponly,
        max_age=cookie_max_age,
        path=cookie_path,
        samesite=cookie_samesite,
        secure=True)
        logger.debug(response.headers)

