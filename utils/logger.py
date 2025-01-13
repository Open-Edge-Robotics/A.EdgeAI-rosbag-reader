import logging


class Logger:
    def __init__(self, name, level=logging.INFO):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(level)
        self.formatter = logging.Formatter(
            "%(asctime)s - %(filename)s - %(lineno)s - %(levelname)s:\n %(message)s"  # noqa
        )
        self.console_handler = logging.StreamHandler()
        self.console_handler.setFormatter(self.formatter)
        self.logger.addHandler(self.console_handler)

    def get_logger(self):
        return self.logger

    def set_level(self, level: int = logging.DEBUG):
        self.logger.setLevel(level)
        self.console_handler.setLevel(level)
        return self.logger

    def set_formatter(self, formatter):
        self.console_handler.setFormatter(formatter)
        return self.logger

    def info(self, message: str):
        self.logger.info(message)

    def debug(self, message: str):
        self.logger.debug(message)

    def warning(self, message: str):
        self.logger.warning(message)

    def error(self, message: str):
        self.logger.error(message)

    def critical(self, message: str):
        self.logger.critical(message)

    def exception(self, message: str):
        self.logger.exception(message)
