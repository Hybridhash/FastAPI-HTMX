import uuid
from typing import Annotated, Optional

from fastapi_users import schemas
from pydantic import UUID4, BaseModel, ConfigDict, EmailStr, Field, StringConstraints

from .pydantic_base import pydantic_partial

PasswordStr = Annotated[str, StringConstraints(strip_whitespace=True, min_length=8)]


class UserRead(schemas.BaseUser[uuid.UUID]):
    email: EmailStr

    class Config:
        # Exclude the unwanted fields from the schema
        json_schema_extra = {
            "example": {
                "email": "user@example.com",
            }
        }


class UserCreate(schemas.BaseUserCreate):
    email: EmailStr
    # Applying constrains on the new user created with minimum length of password
    password: PasswordStr

    class Config:
        # Exclude the unwanted fields from the schema
        json_schema_extra = {
            "example": {"email": "user@example.com", "password": "strings"}
        }


class UserUpdate(schemas.BaseUserUpdate):
    # Applying constrains on the new user created with minimum length of password
    password: PasswordStr

    class Config:
        # Exclude the unwanted fields from the schema
        json_schema_extra = {"example": {"password": "strings"}}


class RoleBase(BaseModel):
    model_config = ConfigDict(hide_input_in_errors=True)

    role_name: str = Field(
        ...,
        title="Role Name",
        description="Role Name",
        min_length=3,
        max_length=50,
    )
    role_desc: Annotated[
        Optional[str],
        Field(
            min_length=5,
            max_length=200,
            examples=["Role description is provided here"],
            title="Role Description",
            default=None,
        ),
    ]
    role_id: UUID4 = Field(
        default_factory=uuid.uuid4,
        title="Role ID",
        description="Role ID",
    )

    # @validator("role_desc")
    # def validate_role_desc(cls, v):
    #     if v == "":
    #         return None
    #     elif len(v) < 5:
    #         raise ValueError("String should have at least 5 characters")
    #     return v


# Pydantic model to read the role based on id and excluding the role_name and role_desc
RoleRead = pydantic_partial(exclude_fields=["role_name", "role_desc"])(RoleBase)
# Pydantic model to create the Role with the role_name and role_desc and excluding the id
RoleCreate = pydantic_partial(exclude_fields=["role_id"])(RoleBase)


class RoleUpdate(RoleBase):
    pass


# class CreateUpdateDictModel(BaseModel):
#     def create_update_dict(self):
#         return model_dump(
#             self,
#             exclude_unset=True,
#             exclude={
#                 "id",
#                 "is_superuser",
#                 "is_active",
#                 "is_verified",
#                 "oauth_accounts",
#             },
#         )
