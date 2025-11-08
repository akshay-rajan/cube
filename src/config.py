import click
import traceback as tb
from functools import wraps
from src.logger import logger

@click.group()
def cli():
    pass

def error_handler(func):
    """Decorator to catch and log errors"""
    
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            logger.error(f"Exception occured: {e}")
            logger.debug(tb.format_exc())

    return wrapper
