import uuid

import nh3
from fastapi import Depends, File, HTTPException, Request, UploadFile
from fastapi.responses import HTMLResponse
from fastapi.routing import APIRouter

from app.core.minio import minio
from app.database.db import CurrentAsyncSession
from app.database.security import current_active_user
from app.models.uploads import Uploads as UploadsModelDB
from app.models.users import User as UserModelDB
from app.routes.view.errors import handle_error
from app.routes.view.view_crud import SQLAlchemyCRUD
from app.schema.uploads import FileCreate

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
        file_extension = file.filename.split(".")[-1]
        unique_name = f"{uuid.uuid4()}.{file_extension}"

        file_url = await minio.upload_file(file, unique_name)
        if file_url.startswith("Error occurred:"):
            raise HTTPException(status_code=500, detail=file_url)

        form = await request.form()

        file_create = FileCreate(
            name=nh3.clean(str(file.filename)),
            unique_name=unique_name,
            file_type=nh3.clean(str(file.content_type)),
            source=nh3.clean(str(form.get("source"))),
            file_size=file.size,
            user_id=current_user.id,
        )

        await upload_crud.create(dict(file_create), db)

        return f"File uploaded successfully. URL: {file_url}"
    except Exception as e:
        return handle_error("partials/upload/upload_file.html", {"request": request}, e)
