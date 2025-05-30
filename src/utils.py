import yaml
import time
import functools
from typing import Any, Callable, TypeVar, Optional
import logging
from .logger import setup_logger

logger = setup_logger(__name__)

T = TypeVar('T')

def load_config(path: str = "config.yaml") -> dict:
    """Load configuration from YAML file."""
    try:
        with open(path, 'r') as f:
            return yaml.safe_load(f)
    except Exception as e:
        logger.error(f"Failed to load config from {path}: {str(e)}")
        raise

def retry_with_backoff(
    retries: int = 3,
    backoff_in_seconds: int = 1,
    max_backoff_in_seconds: int = 60,
    exponential_base: int = 2,
    logger: Optional[logging.Logger] = None
) -> Callable:
    """
    Retry decorator with exponential backoff.
    
    Args:
        retries: Maximum number of retries
        backoff_in_seconds: Initial backoff time in seconds
        max_backoff_in_seconds: Maximum backoff time in seconds
        exponential_base: Base for exponential backoff
        logger: Optional logger instance
    """
    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> T:
            x = 0
            while True:
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    if x == retries:
                        if logger:
                            logger.error(f"Max retries ({retries}) reached. Error: {str(e)}")
                        raise
                    
                    sleep_time = min(
                        backoff_in_seconds * (exponential_base ** x),
                        max_backoff_in_seconds
                    )
                    
                    if logger:
                        logger.warning(
                            f"Attempt {x + 1}/{retries} failed. "
                            f"Retrying in {sleep_time} seconds. Error: {str(e)}"
                        )
                    
                    time.sleep(sleep_time)
                    x += 1
        return wrapper
    return decorator

def validate_phone_number(phone: str) -> bool:
    """
    Validate phone number format.
    
    Args:
        phone: Phone number to validate
        
    Returns:
        bool: True if valid, False otherwise
    """
    # Remove any non-digit characters
    digits = ''.join(filter(str.isdigit, phone))
    
    # Check if it's a valid length (10 digits for US numbers)
    if len(digits) != 10:
        return False
    
    # Check if it starts with a valid US area code
    area_code = int(digits[:3])
    if area_code < 200 or area_code > 999:
        return False
    
    return True

def format_phone_number(phone: str) -> str:
    """
    Format phone number to E.164 format.
    
    Args:
        phone: Phone number to format
        
    Returns:
        str: Formatted phone number
    """
    # Remove any non-digit characters
    digits = ''.join(filter(str.isdigit, phone))
    
    # Add country code if not present
    if len(digits) == 10:
        return f"+1{digits}"
    elif len(digits) == 11 and digits.startswith('1'):
        return f"+{digits}"
    
    return f"+{digits}"
