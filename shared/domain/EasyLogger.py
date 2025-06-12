import logging
import sys
from logging import DEBUG

from .EasyLoggerSingletonMeta import EasyLoggerSingletonMeta


class EasyLogger(metaclass=EasyLoggerSingletonMeta):
    def __init__(self):
        print("Initializing EasyLogger")
        self.__logger = logging.getLogger()
        self.__logger.setLevel(DEBUG)

        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(DEBUG)

        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        console_handler.setFormatter(formatter)

        self.__logger.addHandler(console_handler)

    def info(self, message: str):
        self.__logger.info(message)

    def debug(self, message: str):
        self.__logger.debug(message)

    def warn(self, message: str):
        self.__logger.warning(message)

    def error(self, message: str):
        self.__logger.error(message)
