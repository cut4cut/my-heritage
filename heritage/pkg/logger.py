import json
import logging


class BusinessLogger:
    def __init__(self, name: str):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.INFO)

        self.handler = logging.StreamHandler()
        self.formatter = logging.Formatter(
            '{"time": "%(asctime)s", "name": "%(name)s", "level": "%(levelname)s", "message": %(message)s}'
        )

        self.handler.setFormatter(self.formatter)
        self.logger.addHandler(self.handler)

    def info(self, **kwargs) -> None:
        self.logger.info(json.dumps(kwargs))

    def error(self, **kwargs) -> None:
        self.logger.error(json.dumps(kwargs))
