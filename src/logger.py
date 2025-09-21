import logging

class ColorFormatter(logging.Formatter):
    ASCII_CODES = {
        "reset": "\033[0m",
        "cyan": "\033[36m",
        "green": "\033[32m",
        "yellow": "\033[33m",
        "red": "\033[31m",
        "bold_red": "\033[1;31m",   
    }
    COLORS = {
        "DEBUG": ASCII_CODES["cyan"],
        "INFO": ASCII_CODES["green"],
        "WARNING": ASCII_CODES["yellow"],
        "ERROR": ASCII_CODES["red"],
        "CRITICAL": ASCII_CODES["bold_red"],
    }
    RESET = ASCII_CODES["reset"]

    def format(self, record):
        log_color = self.COLORS.get(record.levelname, self.RESET)
        message = super().format(record)
        return f"{log_color}{message}{self.RESET}"

handler = logging.StreamHandler()
handler.setFormatter(
    ColorFormatter(
        "%(asctime)s - %(levelname)s - %(name)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )
)

logger = logging.getLogger("cube")
logger.setLevel(logging.DEBUG)
logger.addHandler(handler)

logger.info("""
         _       
 ___ _ _| |_ ___ 
|  _| | | . | -_|
|___|___|___|___|
""")
