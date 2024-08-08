from bots.common.exceptions import ValidationError
from datetime import datetime
import re

class Parameter:
    """
    A class to represent a configurable parameter with validation rules.

    :param name: The name of the parameter.
    :type name: str
    :param param_type: The expected type of the parameter (e.g., str, int, datetime).
    :type param_type: type
    :param rules: Arbitrary keyword arguments representing validation rules.
    :type rules: dict

    **Validation Rules**:
        - **required** (:class:`bool`): Whether the parameter is required. Default is False.
        - **default**: A default value to assign if the parameter is not provided.
        - **min_length** (:class:`int`): Minimum length for string parameters.
        - **max_length** (:class:`int`): Maximum length for string parameters.
        - **regex** (:class:`str`): A regular expression pattern that the parameter must match.
        - **min** (:class:`int` or :class:`float`): Minimum value for numeric parameters.
        - **max** (:class:`int` or :class:`float`): Maximum value for numeric parameters.
        - **in** (:class:`list`): A list of allowed values for the parameter.
        - **not_in** (:class:`list`): A list of disallowed values for the parameter.
        - **format** (:class:`str`): Expected date format (for datetime parameters).
        - **before** (:class:`str`): The date must be before this value (for datetime parameters).
        - **after** (:class:`str`): The date must be after this value (for datetime parameters).
        - **transform** (:class:`function`): A function to transform the value before validation.
        - **unique_items** (:class:`bool`): Ensures all items in a list are unique.
        - **min_items** (:class:`int`): Minimum number of items for list parameters.
        - **max_items** (:class:`int`): Maximum number of items for list parameters.
        - **custom_validator** (:class:`function`): A function to apply custom validation logic.

    :Example:

    >>> username_param = Parameter(
    ...     name="username",
    ...     param_type=str,
    ...     required=True,
    ...     min_length=3,
    ...     max_length=20,
    ...     regex=r"^[a-zA-Z0-9_]+$"
    ... )

    """

    def __init__(self, name, param_type, **rules):
        """
        Initializes a new Parameter instance.

        :param name: The name of the parameter.
        :type name: str
        :param param_type: The expected type of the parameter.
        :type param_type: type
        :param rules: Arbitrary keyword arguments representing validation rules.
        :type rules: dict
        """
        self.name = name
        self.param_type = param_type
        self.rules = rules
        self.value = None 

    def validate(self, value):
        """
        Validates the parameter value against the defined rules.

        :param value: The value to validate.
        :type value: varies based on param_type
        :raises ValidationError: If the value fails validation.
        :raises TypeError: If the value is not of the expected type.
        :return: True if the value is valid.
        :rtype: bool
        """
        # Apply transformations if any
        if "transform" in self.rules:
            value = self.rules["transform"](value)

        # Assign default if value is None
        if value is None:
            value = self.rules.get("default", value)

        if not self.rules.get("required", False) and value is None:
            return True

        if self.rules.get("required", False) and value is None:
            raise ValidationError(f"{self.name} is required.")
        
        if not isinstance(value, self.param_type):
            raise ValidationError(f"{self.name} must be of type {self.param_type.__name__}.")
        
        # Length validations for strings
        if "min_length" in self.rules and len(value) < self.rules["min_length"]:
            raise ValidationError(f"{self.name} must be at least {self.rules['min_length']} characters long.")
        
        if "max_length" in self.rules and len(value) > self.rules["max_length"]:
            raise ValidationError(f"{self.name} cannot be more than {self.rules['max_length']} characters long.")
        
        # Regular expression validation
        if "regex" in self.rules and not re.match(self.rules["regex"], value):
            raise ValidationError(f"{self.name} does not match the required format.")
        
        # Range validations for numbers
        if "min" in self.rules and value < self.rules["min"]:
            raise ValidationError(f"{self.name} must be at least {self.rules['min']}.")
        
        if "max" in self.rules and value > self.rules["max"]:
            raise ValidationError(f"{self.name} cannot be more than {self.rules['max']}.")
        
        # Allowed and disallowed values
        if "in" in self.rules and value not in self.rules["in"]:
            raise ValidationError(f"{self.name} must be one of {self.rules['in']}.")
        
        if "not_in" in self.rules and value in self.rules["not_in"]:
            raise ValidationError(f"{self.name} cannot be one of {self.rules['not_in']}.")
        
        # Date format and range validation
        if self.param_type is datetime:
            date_format = self.rules.get("format", "%Y-%m-%d")
            try:
                datetime.strptime(value, date_format)
            except ValueError:
                raise ValidationError(f"{self.name} does not match the date format {date_format}.")
            
            if "before" in self.rules and datetime.strptime(value, date_format) >= datetime.strptime(self.rules["before"], date_format):
                raise ValidationError(f"{self.name} must be before {self.rules['before']}.")
            
            if "after" in self.rules and datetime.strptime(value, date_format) <= datetime.strptime(self.rules["after"], date_format):
                raise ValidationError(f"{self.name} must be after {self.rules['after']}.")

        # Unique items in list validation
        if "unique_items" in self.rules and isinstance(value, list):
            if len(value) != len(set(value)):
                raise ValidationError(f"Items in {self.name} must be unique.")
        
        # Min/max items in list validation
        if isinstance(value, list):
            if "min_items" in self.rules and len(value) < self.rules["min_items"]:
                raise ValidationError(f"{self.name} must contain at least {self.rules['min_items']} items.")
            if "max_items" in self.rules and len(value) > self.rules["max_items"]:
                raise ValidationError(f"{self.name} cannot contain more than {self.rules['max_items']} items.")
        
        # Custom validation logic
        if "custom_validator" in self.rules:
            custom_validator = self.rules["custom_validator"]
            if not custom_validator(value):
                raise ValidationError(f"{self.name} failed custom validation.")

        self.value = value
        return True
