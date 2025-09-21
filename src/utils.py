from src.logger import logger
from src.constants import NAME


def set_head(branch: str):
    """Sets the head to point to a branch"""
    with open(f".{NAME}/HEAD", "w") as file:
        file.write(f"ref: refs/heads/{branch}")
    logger.info(f"HEAD set to refs/heads/{branch}")
