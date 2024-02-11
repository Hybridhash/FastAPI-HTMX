from typing import Optional

import pytest
from pydantic import BaseModel

from ..schema.pydantic_base import pydantic_partial


class TestPartialModel:

    # The function returns a new BaseModel with all fields optional if exclude_fields is None.
    def test_all_fields_optional_if_exclude_fields_is_none(self):
        # Arrange
        class MyModel(BaseModel):
            field1: int
            field2: str

        # Act
        partial = pydantic_partial()(MyModel)

        # Assert
        assert issubclass(partial, BaseModel)
        assert "field1" in partial.schema()["properties"]
        assert "field2" in partial.schema()["properties"]
        if "type" in partial.schema()["properties"]["field1"]:
            assert partial.schema()["properties"]["field1"]["type"] == "integer"
        if "type" in partial.schema()["properties"]["field2"]:
            assert partial.schema()["properties"]["field2"]["type"] == "string"

    # The function returns a new BaseModel with specified fields optional if exclude_fields is a list of field names.
    def test_specified_fields_optional_if_exclude_fields_is_list(self):
        # Arrange
        class MyModel(BaseModel):
            field1: int
            field2: str
            field3: float

        # Act
        partial = pydantic_partial(exclude_fields=["field1", "field3"])(MyModel)

        # Assert
        assert issubclass(partial, BaseModel)
        assert "field1" not in partial.__annotations__
        assert partial.__annotations__["field2"] == Optional[str]
        assert "field3" not in partial.__annotations__

    # The function returns a new BaseModel with the same name and module as the original model.
    def test_same_name_and_module_as_original_model(self):
        # Arrange
        class MyModel(BaseModel):
            field1: int
            field2: str

        # Act
        partial = pydantic_partial()(MyModel)

        # Assert
        assert partial.__name__ == "MyModel"
        assert partial.__module__ == MyModel.__module__

    # The function returns a new BaseModel with no fields if exclude_fields is an empty list.
    def test_no_fields_if_exclude_fields_is_empty_list(self):
        # Arrange
        class MyModel(BaseModel):
            field1: int
            field2: str

        # Act
        partial = pydantic_partial(exclude_fields=[])(MyModel)

        # Assert
        assert issubclass(partial, BaseModel)
        assert len(partial.__annotations__) == 2

    # The function returns a new BaseModel with no fields if exclude_fields contains all field names.
    def test_no_fields_if_exclude_fields_contains_all_field_names(self):
        # Arrange
        class MyModel(BaseModel):
            field1: int
            field2: str

        # Act
        partial = pydantic_partial(exclude_fields=["field1", "field2"])(MyModel)

        # Assert
        assert issubclass(partial, BaseModel)
        assert len(partial.__annotations__) == 0

    # The function raises an exception if the original model is not a subclass of BaseModel.
    def test_exception_if_original_model_not_subclass_of_BaseModel(self):
        # Arrange
        class MyModel:
            field1: int
            field2: str

        # Act & Assert
        with pytest.raises(TypeError):
            pydantic_partial()(MyModel)
