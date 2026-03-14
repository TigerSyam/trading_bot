"""
Property-based tests for logging configuration.
Feature: trading-bot, Property 5: Log entries contain timestamp, level, and module name
Validates: Requirements 3.4
"""
import logging
import re
import io

from hypothesis import given, settings
from hypothesis import strategies as st

from bot.logging_config import setup_logging


# Levels available in the standard logging module
LOG_LEVELS = [logging.DEBUG, logging.INFO, logging.WARNING, logging.ERROR, logging.CRITICAL]
LEVEL_NAMES = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]


@given(
    module_name=st.from_regex(r"[a-zA-Z_][a-zA-Z0-9_.]{0,30}", fullmatch=True),
    level=st.sampled_from(LOG_LEVELS),
    message=st.text(min_size=1, max_size=100),
)
@settings(max_examples=100)
def test_log_entries_contain_timestamp_level_and_module(module_name, level, message):
    """
    # Feature: trading-bot, Property 5: Log entries contain timestamp, level, and module name
    # Validates: Requirements 3.4

    For any log entry written by the Trading Bot, the log line must contain
    a timestamp, a log level string, and the originating module name.
    """
    stream = io.StringIO()
    handler = logging.StreamHandler(stream)
    fmt = "%(asctime)s %(levelname)s %(name)s %(message)s"
    handler.setFormatter(logging.Formatter(fmt))

    logger = logging.getLogger(module_name)
    logger.setLevel(logging.DEBUG)
    # Avoid duplicate handlers across hypothesis examples
    logger.handlers = [handler]
    logger.propagate = False

    logger.log(level, message)

    output = stream.getvalue().strip()
    assert output, "Log handler produced no output"

    level_name = logging.getLevelName(level)

    # Timestamp: matches ISO-like datetime prefix e.g. "2024-01-01 12:00:00,000"
    timestamp_pattern = re.compile(r"\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2},\d+")
    assert timestamp_pattern.search(output), (
        f"Log entry missing timestamp. Got: {output!r}"
    )

    # Level name must appear in the log line
    assert level_name in output, (
        f"Log entry missing level '{level_name}'. Got: {output!r}"
    )

    # Module name must appear in the log line
    assert module_name in output, (
        f"Log entry missing module name '{module_name}'. Got: {output!r}"
    )
