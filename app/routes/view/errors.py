from typing import Dict, Union

from fastapi import HTTPException
from loguru import logger
from pydantic import ValidationError

from app.templates import templates


def handle_error(
    template: str,
    context: Dict,
    error: Union[ValidationError, HTTPException, Exception],
) -> templates.TemplateResponse:
    """
    Handles errors that occur during the processing of a request, and returns a template
    response with the appropriate error messages.

    Args:
        template (str): The name of the template to render.
        context (dict): This is a dictionary containing the data that will be passed to the template.
        It should include the request object and any database objects that need to be rendered in the template.
        For example, you might pass {"request": request, "group": await group_crud.read_by_primary_key(db, group_id)} as the context.
        error (Exception): This is the exception that was raised during the execution of your code.

    Returns:
        A FastAPI response containing the rendered template with the error messages.
    """
    logger.info(f"context: {context}, error: {error}")
    error_messages: list[str] = []
    if isinstance(error, ValidationError):
        if error.errors():
            error_messages = [
                f"{str(err['loc']).strip('(),')}: {err['msg']}"
                for err in error.errors()
            ]
        else:
            error_messages = ["An unexpected validation error occurred"]
    elif isinstance(error, HTTPException):
        error_messages = [error.detail]
    else:
        error_messages = ["An unexpected error occurred: {}".format(error)]

    context["error_messages"] = error_messages
    logger.info(error_messages)
    return templates.TemplateResponse(template, context)
