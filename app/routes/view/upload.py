import json
import uuid
from urllib.parse import parse_qs, unquote_plus

import nh3
from fastapi import Depends, File, HTTPException, Request, UploadFile
from fastapi.responses import HTMLResponse, StreamingResponse
from fastapi.routing import APIRouter

from app.core.minio_core import minio
from app.database.db import CurrentAsyncSession
from app.database.security import current_active_user
from app.models.upload import Upload as UploadsModelDB
from app.models.users import User as UserModelDB
from app.routes.view.errors import handle_error
from app.routes.view.view_crud import SQLAlchemyCRUD
from app.schema.uploads import FileCreate
from app.templates import templates

upload_crud = SQLAlchemyCRUD[UploadsModelDB](UploadsModelDB)
upload_view_route = APIRouter()


@upload_view_route.get("/get_upload_file", response_class=HTMLResponse)
async def get_upload_file(
    request: Request,
    db: CurrentAsyncSession,
    current_user: UserModelDB = Depends(current_active_user),
):
    if not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="Not authorized to upload files")
    try:
        return templates.TemplateResponse(
            "pages/upload.html",
            {
                "request": request,
                "current_user": current_user,
                "user_type": current_user.is_superuser,
            },
        )
    except Exception as e:
        return await handle_error(
            "pages/upload.html",
            {
                "request": request,
                "user_type": current_user.is_superuser,
                "current_user": current_user,
            },
            e,
        )


@upload_view_route.post("/post_upload_file", response_class=HTMLResponse)
async def post_upload_file(
    request: Request,
    db: CurrentAsyncSession,
    current_user: UserModelDB = Depends(current_active_user),
    file: UploadFile = File(...),
):

    try:
        if not current_user.is_superuser:
            raise HTTPException(
                status_code=403, detail="Not authorized to upload files"
            )
        if file.filename is None:
            raise HTTPException(status_code=400, detail="Filename is missing")
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

        headers = {
            "HX-Trigger": json.dumps(
                {
                    "showAlert": {
                        "type": "added",
                        "message": f"{file.filename} uploaded successfully. URL: {file_url}",
                        "source": "upload-page",
                    },
                    "refreshUploadTable": "",
                }
            ),
        }
        return HTMLResponse(content="", headers=headers)
    except Exception as e:
        return handle_error("pages/upload.html", {"request": request}, e)


# Making a route to get the uploaded files
@upload_view_route.get("/get_uploaded_files", response_class=HTMLResponse)
async def get_uploaded_files(
    request: Request,
    db: CurrentAsyncSession,
    current_user: UserModelDB = Depends(current_active_user),
    skip: int = 0,
    limit: int = 100,
):
    if not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="Not authorized to view files")
    try:
        files = await upload_crud.read_by_column(
            db, "user_id", current_user.id, skip, limit
        )
        return templates.TemplateResponse(
            "partials/upload/files_table.html",
            {
                "request": request,
                "files": files,
                "current_user": current_user,
                "user_type": current_user.is_superuser,
            },
        )
    except Exception as e:
        return handle_error("partials/upload/files_table.html", {"request": request}, e)


# Route to download a file from the back end
@upload_view_route.get("/download/{file_unique_name}")
async def download_file(
    request: Request,
    file_unique_name: str,
    db: CurrentAsyncSession,
    current_user: UserModelDB = Depends(current_active_user),
):
    if not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="Not authorized to download files")
    try:

        file_response = await minio.get_file(file_unique_name)

        if isinstance(file_response, str):
            raise HTTPException(status_code=500, detail=file_response)
        return StreamingResponse(
            file_response,
            media_type="application/octet-stream",
            headers={"Content-Disposition": f"attachment; filename={file_unique_name}"},
        )
    except Exception as e:
        return handle_error("pages/upload.html", {"request": request}, e)


# Route to delete a file from the back end
@upload_view_route.delete("/delete/{file_unique_name}")
async def delete_file(
    request: Request,
    file_unique_name: str,
    db: CurrentAsyncSession,
    current_user: UserModelDB = Depends(current_active_user),
    response=HTMLResponse,
):

    try:
        if not current_user.is_superuser:
            raise HTTPException(
                status_code=403, detail="Not authorized to delete files"
            )

        extra_info = await request.body()

        parsed_values = parse_qs(unquote_plus(extra_info.decode()))

        file_id = uuid.UUID(parsed_values["file_id"][0])

        file_response = await minio.remove_file(file_unique_name)
        if file_response.startswith("Error occurred:"):
            raise HTTPException(status_code=500, detail=file_response)
        await upload_crud.delete(db, file_id)
        headers = {
            "HX-Trigger": json.dumps(
                {
                    "showAlert": {
                        "type": "deleted",
                        "message": f"{file_id} deleted successfully.",
                        "source": "upload-page",
                    },
                    "refreshUploadTable": "",
                }
            ),
        }
        return HTMLResponse(content="", headers=headers)
    except Exception as e:
        return handle_error("pages/upload.html", {"request": request}, e)
