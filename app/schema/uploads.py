import uuid
from typing import Annotated, Optional

from pydantic import UUID4, BaseModel, ConfigDict, Field, validator

from .pydantic_base import pydantic_partial


class FileBase(BaseModel):
    model_config = ConfigDict(hide_input_in_errors=True)

    name: str = Field(
        ...,
        title="Name",
        description="Name",
        min_length=3,
        max_length=250,
    )
    unique_name: str = Field(
        ...,
        title="Unique Name",
        description="Unique Name",
        min_length=3,
        max_length=50,
    )
    file_type: str = Field(
        ...,
        title="File Type",
        description="File Type",
    )
    source: Annotated[
        Optional[str],
        Field(
            title="Source",
            description="Source",
        ),
    ]
    file_size: Annotated[
        Optional[int],
        Field(
            title="File Size",
            description="File Size",
        ),
    ]
    user_id: UUID4 = Field(
        default_factory=uuid.uuid4,
        title="User ID",
        description="User ID",
    )

    file_id: UUID4 = Field(
        default_factory=uuid.uuid4,
        title="File ID",
        description="File ID",
    )

    @validator("file_size")
    def validate_file_size(cls, v):
        if v == "":
            return None
        elif v < 0 or v == 0:
            raise ValueError("File size cannot be zero")
        # checking if the file size is greater than 10 MB
        elif v > 10000000:
            raise ValueError("File size cannot be greater than 10 MB")
        return v


FileCreate = pydantic_partial(exclude_fields=["file_id"])(FileBase)
FileRead = pydantic_partial(
    exclude_fields=["user_id", "unique_name", "file_type", "source", "file_size"]
)(FileBase)
