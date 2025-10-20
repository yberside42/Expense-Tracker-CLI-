# validators.py 

from __future__ import annotations
from datetime import date

def validate_date_iso(date_value: str) -> str:
    """Return a string, only if the date format is correct (YYYY-MM-DD).

    Args:
        date_value: String that represents a date.
        
    Raises:
        ValueError: If the date format is invalid or is not a string.

    Returns:
        str: String with a valid date format (ISO).
    """
    # Checking if it is a string.
    if not isinstance(date_value, str):
        raise ValueError("Date must be a string in format: YYYY-MM-DD")
    
    # Checking if it is in ISO format.
    try:
        date.fromisoformat(date_value)
    except Exception:
        raise ValueError(f"Invalid date: {date_value!r}. YYYY-MM-DD was expected.")
    
    return date_value

def validate_amount(amount_value) -> float: 
    """Return an amount as a float if the amount is > 0.

    Args:
        amount_value (int | float | str): Value to validate.
        
    Raises:
        ValueError: if the amount is not numeric or is < 0.

    Returns:
        float: Amount in a float type.
    """
    # Checking if the value is numeric
    try: 
        value = float(amount_value)
    except Exception:
        raise ValueError(f"amount must be numeric; got {amount_value!r}.")
    # Checking if the value is higher than 0. 
    if value <= 0: 
        raise ValueError("amount must be > 0.")
    
    return value

def validate_category(category_str: str) -> str: 
    """Return a normalized category string. 

    Args:
        category_str (str): Category string to normalize.
        
    Raises:
        ValueError: If the category string is empty. 

    Returns:
        str: Normalized category string.
    """
    # Category can't be empty
    if category_str is None:
        raise ValueError("Category is required.")
    
    out = str(category_str).strip()
    if not out:
        raise ValueError("Category cannot be empty.")
    
    return out

def validate_id(id_value) -> int:
    """Return a positive integer ID.

    Args:
        id_value (int | str): ID to validate.

    Raises:
        ValueError: If the ID is not positive or an integer.
        
    Returns:
        int: Positive ID integer. 
    """
    # Checking if the value is an integer
    try: 
        id_int = int(id_value)
    except Exception:
        raise ValueError(f"ID must be an integer. Instead got {id_value!r}")
    # The value must be higher than 0
    if id_int <= 0:
        raise ValueError("ID must be > 0")
    
    return id_int
