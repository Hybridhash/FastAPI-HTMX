
from fastapi import Request
from fastapi.responses import HTMLResponse
from fastapi.routing import APIRouter

from app.templates import templates

# Create an APIRouter
html_view_router = APIRouter()

@html_view_router.get("/", response_class=HTMLResponse)
async def read_item(request: Request):
    return templates.TemplateResponse(
        "index.html",
        {"request": request, "title": "My Web Page", "message": "Welcome to my web page!"},
    )

