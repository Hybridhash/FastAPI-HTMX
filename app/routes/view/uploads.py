from fastapi import Depends, File, HTTPException, Request, UploadFile
from fastapi.responses import HTMLResponse
from fastapi.routing import APIRouter

from app.core.minio import minio
from app.database.db import CurrentAsyncSession
from app.database.security import current_active_user
from app.models.users import User as UserModelDB
from app.models.uploads import Uploads as UploadsModelDB
from app.routes.view.view_crud import SQLAlchemyCRUD

upload_crud = SQLAlchemyCRUD[UploadsModelDB](UploadsModelDB)
uploads_view_route = APIRouter()


@uploads_view_route.post("/upload", response_class=HTMLResponse)
async def upload_file(
    request: Request,
    db: CurrentAsyncSession,
    current_user: UserModelDB = Depends(current_active_user),
    file: UploadFile = File(...),
):
    if not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="Not authorized to upload files")
    try:
        object_name = file.filename
        file_url = await minio.upload_file(file, object_name)
        if file_url.startswith("Error occurred:"):
            raise HTTPException(status_code=500, detail=file_url)
        file_extension = file.filename.split(".")[-1]
        f"{uuid.uuid4()}.{file_extension}"
        return f"File uploaded successfully. URL: {file_url}"
    