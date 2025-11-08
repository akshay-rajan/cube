import os
import pickle
from hashlib import sha1
from fnmatch import fnmatch
from functools import wraps
from src.logger import logger
from src.objects import Commit, Index
from src.constants import NAME


def get_root_path(path: str) -> bool:
    """Checks if the given filepath is at the root of the repository."""
    directory_name = os.path.dirname(path)
    system_root_dir = os.path.abspath(os.sep)
    error = ValueError("The directory is not version controlled!")
    if directory_name == system_root_dir:
        raise error

    vcs_dir_name = f".{NAME}"
    for dir in os.listdir(path):
        if dir == vcs_dir_name:
            return os.path.abspath(path)

    parent_dir = os.path.abspath(os.path.join(directory_name, os.pardir))
    return get_root_path(parent_dir)

def initialization_required(func):
    """Decorator to check if the VCS is already initialized, else raises ValueError"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            get_root_path(".")
        except ValueError:
            logger.error("VCS is not initialized. Please run 'init' command first.")
            return False
        return func(*args, **kwargs)
    return wrapper

def set_head(branch: str):
    """Sets the head to point to a branch"""
    with open(f".{NAME}/HEAD", "w") as file:
        file.write(f"refs/heads/{branch}")
    logger.info(f"HEAD set to refs/heads/{branch}")


def hash_file(filepath: str) -> str:
    """Returns the SHA-1 hash of the file content"""

    sha = sha1()
    with open(filepath, 'rb') as f:
        while chunk := f.read(8192):
            sha.update(chunk)
    return sha.hexdigest()


def get_object_path(file_hash: str) -> str:
    """Returns the path where the object should be stored based on its hash"""
    first_2_chars, remaining_chars = file_hash[:2], file_hash[2:]
    return f".{NAME}/objects/{first_2_chars}/{remaining_chars}"


def is_indexed(index_file, filepath: str) -> bool:
    """
    Checks if a file is already staged.
    If yes, return the line number (1-based) in the index file.
    """
    i = 0
    for line in index_file:
        hash, indexed_path = line.strip().split(" ", 1)
        if indexed_path == filepath:
            return hash, i
        i += 1
    return "", -1


def overwrite_index(filename: str, lines: list, line_number: int, entry: str):
    """Overwrites the hash of a file in the index"""
    lines[line_number - 1] = entry
    with open(filename, "w") as file:
        file.writelines(lines)


def add_object(file_hash: str, filepath: str):
    object_path = get_object_path(file_hash)
    os.makedirs(os.path.dirname(object_path), exist_ok=True)

    with open(filepath, 'rb') as src_file:
        content = src_file.read()
    with open(object_path, 'wb') as obj_file:
        obj_file.write(content)
    logger.info(f"File '{filepath}' stored at {object_path}.")


def delete_object(object_hash: str):
    """
    Deletes an object from the objects directory.
    If the hash is 'a1b2c3...', it deletes the file at '.cube/objects/a1/b2c3...'
    """
    object_path = get_object_path(object_hash)
    if os.path.exists(object_path):
        os.remove(object_path)
        dir_path = os.path.dirname(object_path)
        if not os.listdir(dir_path):
            os.rmdir(dir_path)
        logger.info(f"Deleted previously staged version: {object_path}.")
    else:
        logger.warning(f"Object {object_hash} does not exist at {object_path}.")


def matches_pattern(filepath: str, pattern: str) -> bool:
    """Checks if a filepath matches a given pattern (supports '*' wildcard)"""
    return fnmatch(filepath, pattern)

def store_commit(commit: Commit):
    """Store a commit object in the objects directory."""
    to_bytes = pickle.dumps(commit)
    object_hash = sha1(to_bytes).hexdigest()
    object_path = get_object_path(object_hash)
    os.makedirs(os.path.dirname(object_path), exist_ok=True)
    with open(object_path, 'wb') as obj_file:
        obj_file.write(to_bytes)
    logger.info(f"Commit stored at {object_path}.")
    return object_hash

def store_index(index: Index) -> str:
    """Store an index object in the objects directory."""
    to_bytes = pickle.dumps(index)
    with open(Index.path, 'wb') as obj_file:
        obj_file.write(to_bytes)
    logger.info("Index updated.")

def get_current_branch() -> str:
    """Returns the current branch name from HEAD"""
    with open(f".{NAME}/HEAD", "r") as file:
        ref = file.read().strip()
    if ref.startswith("refs/heads/"):
        return ref[len("refs/heads/"):]
    raise ValueError("HEAD is in a detached state.")


def get_head_commit_hash() -> str:
    """Returns the commit hash that HEAD points to"""
    try:
        with open(f".{NAME}/HEAD", "r") as file:
            ref = file.read().strip()
    except FileNotFoundError:
        return None

    if ref.startswith("refs/heads/"):
        branch = ref[len("refs/heads/"):]
        branch_path = f".{NAME}/refs/heads/{branch}"
        if os.path.isfile(branch_path):
            with open(branch_path, "r") as branch_file:
                commit_hash = branch_file.read().strip()
                return commit_hash if commit_hash else None
        else:
            raise ValueError(f"Branch '{branch}' does not exist.")
    raise ValueError("HEAD is in a detached state.")

def update_branch_pointer(branch_name, commit_hash):
    """Update a branch to point to a new commit"""
    branch_path = f".{NAME}/refs/heads/{branch_name}"
    os.makedirs(os.path.dirname(branch_path), exist_ok=True)
    with open(branch_path, "w") as branch_file:
        branch_file.write(hash)

def branch_exists(branch_name: str):
    """Returns True if the branch already exists, False otherwise"""
    branch_path = f".{NAME}/refs/heads/{branch_name}"
    if os.path.isfile(branch_path):
        return True
    return False
