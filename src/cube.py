import os
import shutil
import click

from src.config import cli, error_handler
from src import utils
from src.logger import logger
from src.commit import Tree, Commit
from src.constants import NAME

ROOT = f".{NAME}"

class Cube:
    """Version Control System"""

    @staticmethod
    @cli.command(name="init")
    @error_handler
    def __init__():
        if not os.path.isdir(ROOT):
            os.mkdir(ROOT)
            os.mkdir(f".{NAME}/objects")
            open(f".{NAME}/index", "w").close()
            os.makedirs(f".{NAME}/refs/heads")
            logger.info("VCS initialized.")
        else:
            logger.info("VCS is already initialized.")
        utils.set_head("main")

    @staticmethod
    def is_initialized() -> bool:
        try:
            utils.get_root_path(".")
            return True
        except ValueError:
            logger.error("VCS is not initialized. Please run 'init' command first.")
            return False

    @staticmethod
    @cli.command()
    @error_handler
    def undo():
        if not Cube.is_initialized():
            return
        shutil.rmtree(ROOT)
        logger.info(f"VCS reset successful.")

    def _stage_file(filepath: str) -> str:
        """Converts a file to a blob and stores it in the objects directory"""

        file_hash = utils.hash_file(filepath)
        object_path = utils.get_object_path(file_hash)

        if not os.path.exists(object_path):
            utils.add_object(file_hash, filepath)

            index_filename = f".{NAME}/index"
            index_entry = f"{file_hash} {filepath}\n"
            
            with open(index_filename, "r") as index_file:
                lines = index_file.readlines()
            
            prev_hash, line_number = utils.is_indexed(lines, filepath)
            if prev_hash:
                utils.overwrite_index(index_filename, lines, line_number, index_entry)
                utils.delete_object(prev_hash)
            else:
                with open(index_filename, "a") as index_file:
                    index_file.write(index_entry)
        else:
            logger.info(f"Blob with hash {file_hash} already exists.")

        return file_hash

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

        Cube._stage_file(filepath)
        logger.info(f"Staged '{filepath}'.")

    @staticmethod
    def _get_ignored_files() -> list:
        ignore_file = f".{NAME}ignore"
        ignored_files = []
        if os.path.isfile(ignore_file):
            with open(ignore_file, "r") as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith("#"):
                        ignored_files.append(line)
        else:
            logger.info(f"No {NAME}ignore file found!.")
        return ignored_files
    
    @staticmethod
    def _is_ignored(filepath: str, ignored_files: list) -> bool:
        if not ignored_files:
            return False
        for pattern in ignored_files:
            if utils.matches_pattern(filepath, pattern):
                return True
        return False

    @staticmethod
    def _get_index():
        with open(f".{NAME}/index", "r") as index_file:
            return index_file.readlines()

    @staticmethod
    @cli.command()
    @error_handler
    def status():
        if not Cube.is_initialized():
            return

        staged = Cube._get_index()
        staged_paths = []
        staged_msg, modified_msg = "", ""

        if not staged:
            logger.info("No files staged.")
        else:
            for entry in staged:
                file_hash, filepath = entry.strip().split(" ", 1)
                staged_paths.append(filepath)
                current_hash = utils.hash_file(filepath) if os.path.isfile(filepath) else None
                file_info = f"{filepath} {file_hash}"
                if current_hash == file_hash:
                    staged_msg += f"\n\t{file_info}"
                else:
                    modified_msg += f"\n\t{file_info} -> {current_hash or 'deleted'}"

        untracked, untracked_msg = [], ""
        ignored_files = Cube._get_ignored_files()
        for root, _, files in os.walk("."):
            for file in files:
                full_path = os.path.relpath(os.path.join(root, file))
                if full_path.startswith(f".{NAME}/") or full_path in staged_paths:
                    continue
                if Cube._is_ignored(full_path, ignored_files):
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

    @staticmethod
    def _add_commit(tree, parent=None, message=None):
        commit = Commit(tree, parent, message)
        utils.store_commit(commit)
        utils.clear_index()

    @staticmethod
    @cli.command()
    @error_handler
    def commit():
        if not Cube.is_initialized():
            return

        index = Cube._get_index()
        if not index:
            logger.info("No files staged for commit.")
            return

        commit_tree = Tree(".")
        for entry in index:
            file_hash, filepath = entry.strip().split(" ", 1)
            commit_tree.add_subtrees(filepath, file_hash)
        logger.debug(f"Commit tree: \n{commit_tree}")

        Cube._add_commit(commit_tree)
