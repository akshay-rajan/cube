import os
import shutil
import click

from src.config import cli, error_handler
from src.utils import set_head, stage_file, hash_file
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
    def is_initialized() -> bool:
        if not os.path.isdir(f".{NAME}"):
            logger.error("VCS is not initialized. Please run 'init' command first.")
            return False
        return True

    @staticmethod
    @cli.command()
    @error_handler
    def undo():
        if not Cube.is_initialized():
            return
        shutil.rmtree(f".{NAME}")
        logger.info(f"VCS reset successful.")

    @staticmethod
    @cli.command()
    @click.argument("filepath")
    @error_handler
    def add(filepath: str):
        if not Cube.is_initialized():
            return
        if not os.path.isfile(filepath):
            logger.error(f"File '{filepath}' does not exist.")
            return

        stage_file(filepath)
        logger.info(f"Staged '{filepath}'.")

    @staticmethod
    @cli.command()
    @error_handler
    def status():
        if not Cube.is_initialized():
            return

        with open(f".{NAME}/index", "r") as index_file:
            staged = index_file.readlines()

        staged_paths = []
        staged_msg, modified_msg = "", ""

        if not staged:
            logger.info("No files staged.")
        else:
            for entry in staged:
                file_hash, filepath = entry.strip().split(" ", 1)
                staged_paths.append(filepath)
                current_hash = hash_file(filepath) if os.path.isfile(filepath) else None
                file_info = f"{filepath} {file_hash}"
                if current_hash == file_hash:
                    staged_msg += f"\n\t{file_info}"
                else:
                    modified_msg += f"\n\t{file_info} -> {current_hash or 'deleted'}"

        untracked, untracked_msg = [], ""
        for root, _, files in os.walk("."):
            for file in files:
                full_path = os.path.relpath(os.path.join(root, file))
                if full_path.startswith(f".{NAME}/") or full_path in staged_paths:
                    continue
                untracked.append(full_path)
        
        untracked_msg += "\nUntracked files:"
        for file in untracked:
            untracked_msg += f"\n\t{file}"
        
        if staged_msg:
            logger.info(f"\nStaged: {staged_msg}")
        if modified_msg:
            logger.error(f"\nModified: {modified_msg}")
        if untracked:
            logger.debug(untracked_msg)

        msg = (
            f"\nTotal {len(staged)} file(s) staged."
            f"\nHEAD is at {open(f'.{NAME}/HEAD').read().strip()}."
        )
        logger.warning(msg)
