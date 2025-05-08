import logging
import time

from logging.handlers import RotatingFileHandler

class UTCFormatter(logging.Formatter):
    def formatTime(self, record, datefmt=None):
        ct = time.gmtime(record.created)
        return time.strftime("%Y-%m-%d %H:%M:%S", ct)

logger = logging.getLogger("webserver")
logger.setLevel(logging.INFO)

handler = RotatingFileHandler("webserver.log", maxBytes = 1024*1024, backupCount = 5)
formatter = UTCFormatter("[%(asctime)s] [%(levelname)s] - %(message)s")
handler.setFormatter(formatter)

if not logger.hasHandlers():
    logger.addHandler(handler)
