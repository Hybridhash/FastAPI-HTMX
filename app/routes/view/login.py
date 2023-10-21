
from typing import Optional

from fastapi import Depends, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.routing import APIRouter
from loguru import logger

from app.database.security import current_active_user, verify_jwt
from app.models.users import User as UserModelDB
from app.templates import templates

# Create an APIRouter
login_view_route = APIRouter()


# Defining a route to navigate to the dashboard page using the current_active_user dependency
@login_view_route.get("/dashboard", response_class=HTMLResponse)
async def get_dashboard(request: Request, user: UserModelDB = Depends(current_active_user)):
      # Access the cookies using the Request object
    logger.debug(current_active_user)
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
# @login_view_route.post("/login", summary="Logs in a user", tags=["Pages","Authentication"], response_class=HTMLResponse)
# async def post_login(request: Request, response: Response):
#     form = await request.form()
#     username = str(form.get("username"))
#     password = str(form.get("password"))
#     try:
#         httpx_response = await get_login_http(username, password)
#         if httpx_response.status_code == 204:
#             response = RedirectResponse("/", status_code=302)
#             await LoginView.set_cookie(username, password, response)
#             return response
#         else:
#             raise HTTPException(status_code=401, detail="Incorrect username or password")
#     except HTTPException as e:
#         return templates.TemplateResponse("pages/login.html", {"request": request, "error": e.detail})

# Adding a logout view that sets the cookie to expire
# @login_view_route.get("/logout", summary="Logs out a user", tags=["Pages", "Authentication"])
# async def logout(response: Response):
#     response = RedirectResponse("/", status_code=302)
#     response.delete_cookie("fastapiusersauth")
#     return response
        
# class LoginView:
#     @staticmethod
#     async def set_cookie(username:str, password:str, response:Response) -> None:
#         """
#         Sets a cookie for the user's authentication information.

#         Args:
#         - username (str): The user's username.
#         - password (str): The user's password.
#         - response (Response): The response object to set the cookie on.

#         Returns:
#         - None
#         """
#         httpx_response = await get_login_http(username, password)
#         if httpx_response.status_code == 204:
#             cookie = http.cookies.SimpleCookie(httpx_response.headers["set-cookie"])["fastapiusersauth"]
#             cookie_value = cookie.value
#             cookie_httponly = cookie["httponly"]
#             cookie_max_age = cookie["max-age"]
#             cookie_path = cookie["path"]
#             cookie_samesite = cookie["samesite"]

#             response.set_cookie(
#             key="fastapiusersauth",
#             value=cookie_value,
#             httponly=cookie_httponly,
#             max_age=cookie_max_age,
#             path=cookie_path,
#             samesite=cookie_samesite,
#             secure=True)
#         else:
#             raise HTTPException(status_code=401, detail="Incorrect username or password")
