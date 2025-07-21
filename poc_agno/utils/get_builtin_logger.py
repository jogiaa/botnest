import logging


def get_builtin_logger(name: str = "SCRIBE") -> logging.Logger:
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)
    if not logger.handlers:
        handler = logging.StreamHandler()
        format = '[%(asctime)s[%(name)s][%(levelname)s]-%(process)d] - %(message)s'
        formatter = logging.Formatter(format)
        handler.setFormatter(formatter)
        logger.addHandler(handler)
    return logger


if __name__ == '__main__':
    logger = get_builtin_logger()

    logger.info("those who wish to follow me..")
    logger.debug("I welcome with my hands..")
    logger.error("And the red sun sinks at last...")
    logger.warning("into hills of gold...")
