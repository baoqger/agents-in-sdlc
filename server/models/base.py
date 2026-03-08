# Base model for SQLAlchemy ORM models, providing shared validation logic
# used across all models in the application.
from . import db

class BaseModel(db.Model):
    """Abstract base class for all SQLAlchemy models, providing shared validation helpers."""

    __abstract__ = True
    
    @staticmethod
    def validate_string_length(field_name: str, value: str | None, min_length: int = 2, allow_none: bool = False):
        """Validate that a string field meets minimum length requirements.

        Args:
            field_name (str): Human-readable name of the field, used in error messages.
            value: The value to validate.
            min_length (int): Minimum number of non-whitespace characters required. Defaults to 2.
            allow_none (bool): Whether None is an acceptable value. Defaults to False.

        Returns:
            The original value if validation passes.

        Raises:
            ValueError: If value is None and allow_none is False, not a string,
                        or shorter than min_length after stripping whitespace.
        """
        if value is None:
            if allow_none:
                return value
            else:
                raise ValueError(f"{field_name} cannot be empty")
        
        if not isinstance(value, str):
            raise ValueError(f"{field_name} must be a string")
            
        if len(value.strip()) < min_length:
            raise ValueError(f"{field_name} must be at least {min_length} characters")
            
        return value