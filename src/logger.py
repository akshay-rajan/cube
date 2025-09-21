import logging

class ColorFormatter(logging.Formatter):
    COLORS = {
        "DEBUG": "\033[36m",        # Cyan
        "INFO": "\033[32m",         # Green
        "WARNING": "\033[33m",      # Yellow
        "ERROR": "\033[31m",        # Red
        "CRITICAL": "\033[1;31m",   # Bold Red
    }
    RESET = "\033[0m"

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
