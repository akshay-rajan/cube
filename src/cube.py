import os
import shutil
import click

from src.config import cli, error_handler
from src import utils
from src.logger import logger
from src.objects import Tree, Commit, Index
from src.constants import NAME

ROOT = f".{NAME}"


class VCS:
    """Version Control System"""

    @staticmethod
    @cli.command(name="init")
    @error_handler
    def __init__():
        if not os.path.isdir(ROOT):
            os.mkdir(ROOT)
            os.mkdir(f"{ROOT}/objects")
            Index()
            VCS._create_branch("main")
            utils.set_head("main")
            logger.info("VCS initialized.")
        else:
            logger.info("VCS is already initialized.")

    @staticmethod
    def _is_initialized() -> bool:
        try:
            utils.get_root_path(".")
            return True
        except ValueError:
            logger.error("VCS is not initialized. Please run 'init' command first.")
            return False

    @staticmethod
    def _list_branches() -> list:
        branches = os.listdir(f"{ROOT}/refs/heads")
        current_branch = utils.get_current_branch()
        for branch in branches:
            if branch == current_branch:
                logger.debug(f"* {branch}")
            else:
                logger.info(f"  {branch}")

    @staticmethod
    def _create_branch(branch_name: str):
        if utils.branch_exists(branch_name):
            logger.error(f"Branch '{branch_name}' already exists.")
            return

        current_commit = utils.get_head_commit_hash() or ""
        utils.update_branch_pointer(branch_name, current_commit)
        logger.info(f"Branch '{branch_name}' created.")

    @staticmethod
    @cli.command()
    @click.argument("branch_name", required=False)
    def branch(branch_name: str = None):
        if not VCS._is_initialized():
            return

        if not branch_name:
            VCS._list_branches()
        else:        
            VCS._create_branch(branch_name)

    @staticmethod
    @cli.command()
    @error_handler
    def undo():
        if not VCS._is_initialized():
            return
        shutil.rmtree(ROOT)
        logger.info(f"VCS reset successful.")

    def _stage_file(filepath: str) -> str:
        """Converts a file to a blob and stores it in the objects directory"""

        index = Index(from_file=True)
        ignored_files = VCS._get_ignored_files()
        if VCS._is_ignored(filepath, ignored_files):
            logger.info(f"File '{filepath}' is ignored.")
            return

        if os.path.isdir(filepath):
            for root, _, files in os.walk(filepath):
                for file in files:
                    full_path = os.path.relpath(os.path.join(root, file))
                    if VCS._is_ignored(full_path, ignored_files):
                        continue
                    if os.path.isdir(full_path) or os.path.isfile(full_path):
                        VCS._stage_file(full_path)
            return

        file_hash = utils.hash_file(filepath)
        object_path = utils.get_object_path(file_hash)
        if not os.path.exists(object_path):
            utils.add_object(file_hash, filepath)
            index.overwrite(filepath)
        else:
            logger.info(f"Blob with hash {file_hash} already exists.")

        return file_hash

    @staticmethod
    @cli.command()
    @click.argument("filepath")
    @error_handler
    def add(filepath: str):
        if not VCS._is_initialized():
            return

        if not os.path.isfile(filepath) and not os.path.isdir(filepath):
            logger.error(f"File or directory '{filepath}' does not exist.")
            return

        VCS._stage_file(filepath)
        logger.info("Staged.")

    @staticmethod
    def _get_ignored_files() -> list:
        ignore_file = f"{ROOT}ignore"
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
    def _get_commit(hash) -> Commit:
        commit_path = utils.get_object_path(hash)
        if not os.path.isfile(commit_path):
            logger.error(f"Commit with hash {hash} does not exist.")
            return None
        
        with open(commit_path, "rb") as commit_file:
            commit = Commit.from_bytes(commit_file.read())
            return commit

    @staticmethod
    @cli.command()
    @error_handler
    def status():
        if not VCS._is_initialized():
            return

        index = Index(from_file=True)
        staged = index.list_entries()
        staged_paths = []
        staged_msg, modified_msg = "", ""

        commit_hash = utils.get_head_commit_hash()
        if commit_hash:
            commit = VCS._get_commit(commit_hash)
            logger.debug(f"Last commit tree:\n{commit.tree}\n")

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
        ignored_files = VCS._get_ignored_files()
        root_path = utils.get_root_path(".")
        for root, _, files in os.walk(root_path):
            for file in files:
                full_path = os.path.relpath(os.path.join(root, file))
                file_hash = utils.hash_file(full_path)
                object_path = utils.get_object_path(file_hash)
                if full_path.startswith(f"{ROOT}/") or full_path in staged_paths:
                    continue
                if VCS._is_ignored(full_path, ignored_files):
                    continue
                if os.path.isfile(object_path):
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
            f"\nHEAD is at {open(f'{ROOT}/HEAD').read().strip()}."
        )
        logger.warning(msg)

    @staticmethod
    def _add_commit(tree, parent=None, message=None):
        commit = Commit(tree, parent, message)
        hash = utils.store_commit(commit)
        
        branch_name = utils.get_current_branch()
        utils.update_branch_pointer(branch_name, hash)
        logger.info(f"Committed to branch '{branch_name}' with hash {hash}.")

    @staticmethod
    @cli.command()
    @click.option(
        '--message', '-m', prompt='message', help='Commit message.'
    )
    @error_handler
    def commit(message: str):
        if not VCS._is_initialized():
            return

        index = Index(from_file=True)
        index_entries = index.list_entries()
        if not index_entries:
            logger.info("No files staged for commit.")
            return

        commit_tree = Tree(".")
        for filepath, file_hash in index_entries:
            commit_tree.add_subtrees(filepath, file_hash)
        logger.debug(f"Commit tree: \n{commit_tree}")

        parent_commit_hash = utils.get_head_commit_hash()
        VCS._add_commit(commit_tree, parent_commit_hash, message)
        index.clear()

    @staticmethod
    @cli.command()
    @click.argument("branch")
    @error_handler
    def switch(branch: str):
        if not VCS._is_initialized():
            return

        current_branch = utils.get_current_branch()
        if branch == current_branch:
            logger.info(f"Already on branch '{branch}'.")
            return

        if not utils.branch_exists(branch):
            logger.error(f"Branch '{branch}' does not exist!")
            return
        utils.set_head(branch)

    @staticmethod
    def _log_helper(commit: Commit, hash: str):
        if not commit:
            return
        
        logger.warning(hash)
        logger.info(commit)

        VCS._log_helper(commit.get_parent(), commit.parent)

    @staticmethod
    @cli.command()
    @error_handler
    def log():
        if not VCS._is_initialized():
            return
        
        current_commit_hash = utils.get_head_commit_hash()
        if not current_commit_hash:
            logger.info("No commits yet!")
            return
        
        commit = Commit.from_hash(current_commit_hash)
        VCS._log_helper(commit, current_commit_hash)
