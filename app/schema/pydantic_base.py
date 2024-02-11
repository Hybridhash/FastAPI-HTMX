from copy import deepcopy
from typing import Any, Callable, Optional, Type, TypeVar

from pydantic import BaseModel, create_model
from pydantic.fields import FieldInfo

Model = TypeVar("Model", bound=Type[BaseModel])


def pydantic_partial(
    exclude_fields: Optional[list[str]] = None,
) -> Callable[[Model], Model]:
    """A decorator that create a partial model.

    Args:
        model (Type[BaseModel]): BaseModel model.

    Returns:
        Type[BaseModel]: ModelBase partial model.
    """
    if exclude_fields is None:
        exclude_fields = []

    def wrapper(model: Type[Model]) -> Type[Model]:

        base_model: Type[BaseModel] = model

        if not issubclass(base_model, BaseModel):
            raise TypeError("Model must be a subclass of BaseModel")

        def make_field_optional(
            field: FieldInfo, default: Any = None
        ) -> tuple[Any, FieldInfo]:
            new = deepcopy(field)
            new.default = default
            new.annotation = Optional[field.annotation]
            return new.annotation, new

        if exclude_fields:
            base_model = BaseModel

        return create_model(
            model.__name__,
            __base__=base_model,
            __module__=model.__module__,
            **{
                field_name: make_field_optional(field_info)
                for field_name, field_info in model.model_fields.items()
                if field_name not in exclude_fields
            },  # type: ignore
        )  # type: ignore

    return wrapper
