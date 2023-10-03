import uuid
from typing import Annotated

from fastapi_users import schemas
from pydantic import EmailStr, StringConstraints

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
    pass