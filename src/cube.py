import os
import shutil
import click

from src.config import cli, error_handler
from src.utils import set_head, to_blob
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
            open(f".{NAME}/index", "w").close()
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
        logger.info(f"VCS reset successfull.")

    @staticmethod
    @cli.command()
    @click.argument("filename")
    @error_handler
    def add(filename: str):
        if not os.path.isdir(f".{NAME}"):
            logger.error("VCS is not initialized. Please run 'init' command first.")
            return
        if not os.path.isfile(filename):
            logger.error(f"File '{filename}' does not exist.")
            return

        blob_hash = to_blob(filename)

        with open(f".{NAME}/index", "a") as index_file:
            index_file.write(f"{blob_hash} {filename}\n")

        logger.info(f"File '{filename}' added to staging area.")
