import logging
import os

log_file = os.path.join(os.path.dirname(__file__), "primr.log")

logger = logging.getLogger("primr")
logger.setLevel(logging.DEBUG)

# Prevent adding handlers multiple times if module is reloaded
if not logger.handlers:
    fh = logging.FileHandler(log_file)
    fh.setLevel(logging.DEBUG)

    ch = logging.StreamHandler()
    ch.setLevel(logging.INFO)

    formatter = logging.Formatter('%(asctime)s - [%(levelname)s] - %(message)s')
    fh.setFormatter(formatter)
    ch.setFormatter(formatter)

    logger.addHandler(fh)
    logger.addHandler(ch)
