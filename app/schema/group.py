import uuid
from typing import Annotated, Optional

from pydantic import UUID4, BaseModel, ConfigDict, Field, StringConstraints

PasswordStr = Annotated[str, StringConstraints(strip_whitespace=True, min_length=8)]


class GroupBase(BaseModel):
    model_config = ConfigDict(hide_input_in_errors=True)

    group_name: str = Field(
        ...,
        title="Role Name",
        description="Role Name",
        min_length=3,
        max_length=50,
    )
    group_desc: Annotated[
        Optional[str],
        Field(
            min_length=5,
            max_length=200,
            examples=["Role description is provided here"],
            title="Role Description",
            default=None,
        ),
    ]

    # @validator("role_desc")
    # def validate_role_desc(cls, v):
    #     if v == "":
    #         return None
    #     elif len(v) < 5:
    #         raise ValueError("String should have at least 5 characters")
    #     return v


class GroupRead(GroupBase):
    role_id: UUID4 = Field(
        default_factory=uuid.uuid4,
        title="Role ID",
        description="Role ID",
    )


class GroupCreate(GroupBase):
    pass


class GroupUpdate(GroupBase):
    pass


class GroupUserLink(BaseModel):
    group_id: UUID4 = Field(
        default_factory=uuid.uuid4,
        title="Role ID",
        description="Role ID",
    )
    user_id: UUID4 = Field(
        default_factory=uuid.uuid4, title="User ID", description="User ID"
    )

    # def to_dict(self):
    #     # return self.dict(exclude_unset=True, exclude={"id"})


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
