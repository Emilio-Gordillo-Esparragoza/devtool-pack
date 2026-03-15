import logging
from rich.logging import RichHandler


def get_logger(name: str) -> logging.Logger:
    """Get a configured logger with Rich handler."""
    logger = logging.getLogger(name)
    if not logger.handlers:
        logger.setLevel(logging.INFO)
        handler = RichHandler(
            rich_tracebacks=True,
            show_time=False,
            show_level=False,
            show_path=False,
            markup=True,
        )
        logger.addHandler(handler)
        logger.propagate = False
    return logger
