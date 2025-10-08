import os
from hashlib import sha1
from src.logger import logger
from src.constants import NAME


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

def delete_object(object_hash: str):
    """
    Deletes an object from the objects directory.
    If the hash is 'a1b2c3...', it deletes the file at '.cube/objects/a1/b2c3...'
    """
    object_path = f".{NAME}/objects/{object_hash[:2]}/{object_hash[2:]}"
    if os.path.exists(object_path):
        os.remove(object_path)
        dir_path = os.path.dirname(object_path)
        if not os.listdir(dir_path):
            os.rmdir(dir_path)
        logger.info(f"Deleted previously staged version: {object_path}.")
    else:
        logger.warning(f"Object {object_hash} does not exist at {object_path}.")
