import logging

import pytest
from pydantic import BaseModel

from ..schema.pydantic_base import PydanticDTO

LOGGER = logging.getLogger(__name__)


class MyModel(BaseModel):
    field1: int
    field2: int
    field3: int
    field4: int


class TestPydanticBaseInit:
    def test_init_with_include_fields(self):
        # Arrange
        include_fields = ["field1", "field2"]
        model = MyModel

        # Act
        pydantic_base = PydanticDTO(model=model, include_fields=include_fields)

        # Assert
        assert pydantic_base.model == model
        assert pydantic_base.include_fields == include_fields
        assert pydantic_base.exclude_fields == []

    def test_init_with_exclude_fields(self):
        # Arrange
        exclude_fields = ["field3", "field4"]
        model = MyModel

        # Act
        pydantic_base = PydanticDTO(model=model, exclude_fields=exclude_fields)

        # Assert
        assert pydantic_base.model == model
        assert pydantic_base.include_fields == []
        assert pydantic_base.exclude_fields == exclude_fields

    def test_init_with_no_fields(self):
        # Arrange
        model = MyModel

        # Act
        pydantic_base = PydanticDTO(model=model)

        # Assert
        assert pydantic_base.model == model
        assert pydantic_base.include_fields == []
        assert pydantic_base.exclude_fields == []

    def test_init_with_both_include_and_exclude_fields(self):
        # Arrange
        include_fields = ["field1", "field2"]
        exclude_fields = ["field3", "field4"]
        model = MyModel

        # Act & Assert
        with pytest.raises(
            ValueError, match="Cannot include and exclude fields at the same time."
        ):
            PydanticDTO(
                model=model,
                include_fields=include_fields,
                exclude_fields=exclude_fields,
            )

    # def test_init_with_neither_include_nor_exclude_fields(self):
    #     # Arrange
    #     model = MyModel

    #     # Act & Assert
    #     with pytest.raises(
    #         ValueError, match="Either include or exclude fields must be provided."
    #     ):
    #         PydanticDTO(model=model)

    def test_init_with_missing_fields(self, caplog):
        # Arrange
        model = MyModel
        include_fields = ["field1", "field6"]  # field3 is not defined in MyModel
        # Act & Assert
        with pytest.raises(ValueError):
            LOGGER.debug(f"Missing fields: {ValueError}")
            PydanticDTO(model=model, include_fields=include_fields)()

    # Excluding a field that is not defined in the pydantic model
    def test_exclude_missing_field(self, caplog):
        # Arrange
        model = MyModel
        exclude_fields = ["field3", "field6"]  # field6 is not defined in MyModel
        # Act & Assert
        with pytest.raises(
            ValueError, match="Fields {'field6'} are not defined in the pydantic model."
        ):
            PydanticDTO(model=model, exclude_fields=exclude_fields)()
