"""Common validation utilities for Pydantic schemas."""


def trim_and_validate_string(value: str) -> str:
    """Trim whitespace and validate that string is not empty after trimming.
    
    Args:
        value: The string to validate
        
    Returns:
        The trimmed string
        
    Raises:
        ValueError: If the string is empty or whitespace only
    """
    if value is None:
        return value
    trimmed = value.strip()
    if not trimmed:
        raise ValueError("Field cannot be empty or whitespace only")
    return trimmed
