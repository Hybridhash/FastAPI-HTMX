import uuid
from typing import Annotated

from fastapi_users import schemas
from pydantic import BaseModel, EmailStr, StringConstraints

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
            "example": {
                "email": "user@example.com",
                "password": "strings"
            }
        }


class UserUpdate(schemas.BaseUserUpdate):
    # Applying constrains on the new user created with minimum length of password
    password: PasswordStr
 
    class Config:
    # Exclude the unwanted fields from the schema
        json_schema_extra = {
            "example": {
                "password": "strings"
            }
        }


class RoleBase(BaseModel):
    role_name: str
    role_desc: str


class RoleCreate(RoleBase):
    pass

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
