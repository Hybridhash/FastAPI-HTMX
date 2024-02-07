from typing import Optional

from pydantic import BaseModel


class PydanticDTO:
    """
    A class to clear a pydantic model and return a new model based on exclude or include fields.

    Args:
        model (type[BaseModel]): The pydantic model to be processed.
        include_fields (Optional[list[str]]): A list of field names to be included in the new model.
        exclude_fields (Optional[list[str]]): A list of field names to be excluded from the new model.

    Raises:
        ValueError: If both include_fields and exclude_fields are specified.

    """

    def __init__(
        self,
        model: type[BaseModel],
        include_fields: Optional[list[str]] = None,
        exclude_fields: Optional[list[str]] = None,
    ):
        self.model = model
        # Keeping [] as part of argument might not initialize it
        self.include_fields = include_fields if include_fields is not None else []
        self.exclude_fields = exclude_fields if exclude_fields is not None else []

        if self.include_fields and self.exclude_fields:
            raise ValueError("Cannot include and exclude fields at the same time.")

    def __call__(self) -> BaseModel:
        """
        Take the pydantic model define and return new model based on exclude or include fields.

        Returns:
            BaseModel: The new model based on the specified include or exclude fields.

        """
        if self.include_fields:
            # checking that these fields are defined in pydantic model and return including these only
            fields = set(self.include_fields)
            # Python class attribute __annotation__ is used to get the name and type of class attributes
            missing_fields = fields - set(self.model.__annotations__.keys())
            if missing_fields:
                raise ValueError(
                    f"Fields {missing_fields} are not defined in the pydantic model."
                )
            filtered_fields = {
                k: v for k, v in self.model.__dict__.items() if k in fields
            }
            return self.model(**filtered_fields)
        elif self.exclude_fields:
            # checking that these fields are defined in pydantic model and return excluding these only
            fields = set(self.exclude_fields)
            missing_fields = fields - set(self.model.__annotations__.keys())
            if missing_fields:
                raise ValueError(
                    f"Fields {missing_fields} are not defined in the pydantic model."
                )

            filtered_fields = {
                k: v for k, v in self.model.__dict__.items() if k not in fields
            }
            return self.model(**filtered_fields)
        else:
            return self.model()
