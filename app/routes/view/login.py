
from typing import Optional

from fastapi import Depends, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.routing import APIRouter
from loguru import logger

from app.database.security import current_active_user
from app.models.users import User as UserModelDB
from app.templates import templates

# Create an APIRouter
login_view_route = APIRouter()



@login_view_route.get("/dashboard", response_class=HTMLResponse)
async def get_dashboard(request: Request, user: UserModelDB = Depends(current_active_user)):
      # Access the cookies using the Request object
    logger.debug(user)
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
            # if await verify_jwt(cookie_value):
                return RedirectResponse('/dashboard', status_code=302)
        else:
                return RedirectResponse('/login', status_code=302)
        # else:
        #         return RedirectResponse('/login', status_code=302)

@login_view_route.get("/login",summary="Gets the login page", 
                      tags=["Pages", "Authentication"], response_class=HTMLResponse)
async def get_login(request: Request, invalid: Optional[bool] = None, logged_out: Optional[bool] = None, unauthorized: Optional[bool] = None):
      # Access the cookies using the Request object
    context = {'request': request, 'invalid': invalid, 'logged_out': logged_out, 'unauthorized': unauthorized}
    return templates.TemplateResponse(
        "pages/login.html",
        context
    )

