from __future__ import annotations

import logging


DEFAULT_FORMAT = "%(asctime)s | %(levelname)s | %(name)s | %(message)s"


def configure_logging(level: str = "INFO") -> None:
    """Configure operational logs without enabling prompt/body logging."""
    normalized = level.strip().upper() or "INFO"
    numeric_level = getattr(logging, normalized, None)
    if not isinstance(numeric_level, int):
        raise ValueError(f"invalid log level: {level}")
    logging.basicConfig(level=numeric_level, format=DEFAULT_FORMAT, force=True)
