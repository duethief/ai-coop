"""Logging utility with rich console formatting."""

import logging
import sys
from typing import Optional

try:
    from rich.logging import RichHandler
    from rich.console import Console
    _HAS_RICH = True
except ImportError:
    _HAS_RICH = False

_logger: Optional[logging.Logger] = None


def setup_logger(name: str = "aicoop", level: int = logging.INFO) -> logging.Logger:
    """Setup and return application logger."""
    global _logger
    if _logger is not None:
        return _logger

    logger = logging.getLogger(name)
    logger.setLevel(level)
    logger.handlers.clear()

    if _HAS_RICH:
        console = Console()
        handler = RichHandler(
            console=console,
            show_time=True,
            show_path=False,
            rich_tracebacks=True,
            markup=True
        )
    else:
        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(
            logging.Formatter("[%(asctime)s] [%(levelname)s] %(name)s: %(message)s")
        )

    logger.addHandler(handler)
    logger.propagate = False
    _logger = logger
    return logger


logger = setup_logger()
