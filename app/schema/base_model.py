# from pydantic import BaseModel
# # from pydantic.validators import str_validator
# from typing import Union
# # import regex as re

# # --------------------------------------------------------------------------------
# # Base Model - (Used for Data Validation for data received from the Frontend)
# # --------------------------------------------------------------------------------

# # base model that can be inherited by other models
# class ViewBaseModel(BaseModel):
#     """
#     A base model for views that inherits from the Pydantic BaseModel class.
#     """
#     class Config:
#         """
#         Configuration class for Pydantic BaseModel.
#         - extra: ignore extra fields that are not defined in the model.
#         - anystr_strip_whitespace: strip whitespace from any string types.
#         - use_enum_values: use the enum value instead of the member name.
#         """
#         extra = "ignore"
#         anystr_strip_whitespace = True
#         use_enum_values = True

# # --------------------------------------------------------------------------------
# # Custom Validators - (Used for changing the default validation for data received)
# # --------------------------------------------------------------------------------

# class EmptyStrToNone(str):
   
#     @classmethod
#     def __get_validators__(cls):
#         # yield str_validator
#         yield cls.empty_to_none

#     @classmethod
#     def empty_to_none(cls, val: str) -> Union[None, str]:
#         if val == "":
#             return None
#         return cls(val.strip().lower())
    

# class MobileStr(str):
#     """
#     A custom string class that represents a mobile number.

#     Inherits from the built-in str class and adds validation for Saudi and Pakistan mobile numbers.

#     Args:
#         str (str): The string value of the mobile number.

#     Returns:
#         MobileStr: An instance of the MobileStr class.

#     Raises:
#         AssertionError: If the input string is not a valid Saudi or Pakistan mobile number.
#     """

#     @classmethod
#     def __get_validators__(cls):
#         yield str_validator
#         yield cls.validate

#     @classmethod
#     def validate(cls, val: str) -> str:
#         if val == "":
#             return None

#         # this regex validates Saudi and Pakistan mobile numbers
#         pattern = r"^(05|5|\\+9665|009665|\\+92|0092|03|3)[0-9]{8}$"
#         assert bool(re.fullmatch(pattern, val)), "invalid value for mobile"

#         return cls(val)
    
