import logging


class EasyLogger:

    @staticmethod
    def getLogger(level: int | str, output_stream) -> logging.Logger:
        logger = logging.getLogger()
        logger.setLevel(level)

        console_handler = logging.StreamHandler(output_stream)
        console_handler.setLevel(level)

        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        console_handler.setFormatter(formatter)

        logger.addHandler(console_handler)

        return logger
