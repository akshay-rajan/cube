import os
import shutil

from src.config import cli, error_handler
from src.utils import set_head
from src.logger import logger
from src.constants import NAME

class Cube:
    """Version Control System"""

    @staticmethod
    @cli.command(name="init")
    @error_handler
    def __init__():
        if not os.path.isdir(f".{NAME}"):
            os.mkdir(f".{NAME}")
            os.mkdir(f".{NAME}/objects")
            os.makedirs(f".{NAME}/refs/heads")
            logger.info("VCS initialized.")
        else:
            logger.info("VCS is already initialized.")
        set_head("main")

    @staticmethod
    @cli.command()
    @error_handler
    def undo():
        shutil.rmtree(f".{NAME}")
        logger.info(f"Reset the VCS successfully.")
