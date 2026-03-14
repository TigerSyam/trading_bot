import logging
import logging.handlers
import os


def setup_logging(log_file: str = "logs/trading_bot.log") -> None:
    """Configure rotating file handler and console handler for the trading bot."""
    os.makedirs(os.path.dirname(log_file), exist_ok=True)

    fmt = "%(asctime)s %(levelname)s %(name)s %(message)s"
    formatter = logging.Formatter(fmt)

    root_logger = logging.getLogger()
    root_logger.setLevel(logging.DEBUG)

    # Suppress noisy third-party loggers
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    logging.getLogger("requests").setLevel(logging.WARNING)

    # Rotating file handler — 5 MB per file, keep 3 backups
    file_handler = logging.handlers.RotatingFileHandler(
        log_file, maxBytes=5 * 1024 * 1024, backupCount=3
    )
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)

    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)

    root_logger.addHandler(file_handler)
    root_logger.addHandler(console_handler)
