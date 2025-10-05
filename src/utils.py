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

def stage_file(filepath: str) -> str:
    """Converts a file to a blob and stores it in the objects directory"""

    file_hash = hash_file(filepath)
    # Object path should be <first two chars>/<remaining chars> of the hash
    object_path = f".{NAME}/objects/{file_hash[:2]}/{file_hash[2:]}"

    if not os.path.exists(object_path):
        # Create directories to store the object
        os.makedirs(os.path.dirname(object_path), exist_ok=True)
        
        # Read the file content and store it in the repo as a blob
        with open(filepath, 'rb') as src_file:
            content = src_file.read()
        with open(object_path, 'wb') as obj_file:
            obj_file.write(content)
        logger.info(f"File '{filepath}' stored at {object_path}.")

        # Stage the file by adding it to the index in the format "<hash> <filepath>"
        with open(f".{NAME}/index", "a") as index_file:
            index_file.write(f"{file_hash} {filepath}\n")
    else:
        logger.info(f"Blob with hash {file_hash} already exists.")

    return file_hash
