from fastapi import HTTPException, Request, Response
from fastapi.responses import RedirectResponse
from loguru import logger


async def http_exception_handler(request: Request, exc: HTTPException):
    if exc and exc.status_code == 401:
        return RedirectResponse("/login")
    # elif request.scope.get("path") == "/auth/jwt/login" and exc.status_code == 400:
    #     return templates.TemplateResponse("pages/login.html", {"request": request, "error": "Incorrect username or password"})
    else:
        route = request.scope.get("path")
        method = request.scope.get("method")
        logger.error(
            f"Error in route {method} {route}: {exc.detail} : {exc.status_code}"
        )
        # if route == "/auth/jwt/login" and exc.status_code == 400:
        return Response(content="Error managed via HTTP module", status_code=400)
