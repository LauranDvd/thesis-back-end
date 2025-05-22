import logging
import sys
from logging import DEBUG

from domain.EasyLoggerSingletonMeta import EasyLoggerSingletonMeta


class EasyLogger(metaclass=EasyLoggerSingletonMeta):
    def __init__(self):
        print("Initializing EasyLogger")
        self.logger = logging.getLogger()
        self.logger.setLevel(DEBUG)

        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(DEBUG)

        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        console_handler.setFormatter(formatter)

        self.logger.addHandler(console_handler)

    def info(self, message: str):
        self.logger.info(message)

    def debug(self, message: str):
        self.logger.debug(message)

    def error(self, message: str):
        self.logger.error(message)
