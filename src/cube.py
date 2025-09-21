import os
import shutil

from src.config import cli
import src.utils as utils
from src.logger import logger
from src.constants import NAME

class Cube:
    """Version Control System"""

    @staticmethod
    @cli.command(name="init")
    def __init__():
        try:
            if not os.path.isdir(f".{NAME}"):
                os.mkdir(f".{NAME}")
                os.mkdir(f".{NAME}/objects")
                os.makedirs(f".{NAME}/refs/heads")
                utils.set_head("main")
                logger.info("VCS initialized.")
        except OSError as e:
            logger.error(e)

    @staticmethod
    @cli.command()
    def undo():
        try:
            shutil.rmtree(f".{NAME}")
            logger.info(f"Reset the VCS successfully.")
        except OSError as e:
            logger.error(e)
