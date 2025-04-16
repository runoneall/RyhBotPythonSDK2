import logging


class Logger:
    def __init__(self, quoter: str):
        self.quoter = quoter
        self._init_logger()

    def _init_logger(self):
        self.logger = logging.getLogger(self.quoter)
        self.logger.setLevel(logging.DEBUG)

        if not self.logger.handlers:
            color_map = {
                "PINK": "\033[35m",
                "DEBUG": "\033[94m",
                "INFO": "\033[92m",
                "WARNING": "\033[93m",
                "ERROR": "\033[91m",
                "RESET": "\033[0m",
            }
            log_format = f"[%(levelname)s] [{color_map['PINK']}{self.quoter}{color_map['RESET']}] %(message)s"

            class ColoredFormatter(logging.Formatter):
                def format(self, record):
                    levelname = record.levelname
                    if levelname in color_map:
                        record.levelname = (
                            f"{color_map[levelname]}{levelname}{color_map['RESET']}"
                        )
                    return super().format(record)

            console_handler = logging.StreamHandler()
            formatter = ColoredFormatter(log_format)
            console_handler.setFormatter(formatter)
            self.logger.addHandler(console_handler)

    def debug(self, msg, *args, **kwargs):
        if args or kwargs:
            self.logger.debug(
                msg % args if args else msg.format(*args, **kwargs), **kwargs
            )
        else:
            self.logger.debug(msg, **kwargs)

    def info(self, msg, *args, **kwargs):
        if args or kwargs:
            self.logger.info(
                msg % args if args else msg.format(*args, **kwargs), **kwargs
            )
        else:
            self.logger.info(msg, **kwargs)

    def warning(self, msg, *args, **kwargs):
        if args or kwargs:
            self.logger.warning(
                msg % args if args else msg.format(*args, **kwargs), **kwargs
            )
        else:
            self.logger.warning(msg, **kwargs)

    def error(self, msg, *args, **kwargs):
        if args or kwargs:
            self.logger.error(
                msg % args if args else msg.format(*args, **kwargs), **kwargs
            )
        else:
            self.logger.error(msg, **kwargs)
