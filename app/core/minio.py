import io
from typing import List

from fastapi import UploadFile
from minio import Minio
from minio.error import S3Error

from app.core.minio_settings import settings


class MinioClient:
    def __init__(self):
        self.minio_url = settings.minio_url.replace("http://", "").replace(
            "https://", ""
        )
        self.minio_client = Minio(
            self.minio_url,
            access_key=settings.minio_access_key,
            secret_key=settings.minio_secret_key,
            secure=settings.minio_secure,
        )
        self.bucket_name = settings.minio_bucket

    async def create_bucket(self) -> str:
        try:
            if not self.minio_client.bucket_exists(self.bucket_name):
                self.minio_client.make_bucket(self.bucket_name)
            return f"Bucket '{self.bucket_name}' created successfully"
        except S3Error as err:
            return f"Error occurred: {err}"

    async def upload_file(self, file: UploadFile, object_name: str) -> str:
        try:
            content = await file.read()
            self.minio_client.put_object(
                self.bucket_name, object_name, io.BytesIO(content), length=len(content)
            )
            return f"{settings.minio_url}/{self.bucket_name}/{object_name}"
        except S3Error as err:
            return f"Error occurred: {err}"

    async def get_file(self, object_name: str):
        try:
            return self.minio_client.get_object(self.bucket_name, object_name)
        except S3Error as err:
            return f"Error occurred: {err}"

    async def remove_file(self, object_name: str) -> str:
        try:
            self.minio_client.remove_object(self.bucket_name, object_name)
            return f"File '{object_name}' removed successfully"
        except S3Error as err:
            return f"Error occurred: {err}"

    async def list_files(self) -> List[str]:
        try:
            objects = self.minio_client.list_objects(self.bucket_name)
            return [obj.object_name for obj in objects]
        except S3Error as err:
            return [f"Error occurred: {err}"]


minio = MinioClient()
