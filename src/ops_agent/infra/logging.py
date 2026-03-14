"""Structured logging configuration with run_id correlation."""

import logging
import sys

import structlog


def configure_logging() -> None:
    """Configure structured JSON logging with run_id correlation.

    This sets up structlog to output JSON logs that can be easily
    parsed and filtered by run_id, trace_id, etc.
    """
    structlog.configure(
        processors=[
            structlog.contextvars.merge_contextvars,  # Merge context vars (run_id, trace_id)
            structlog.processors.add_log_level,
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.processors.JSONRenderer(),  # JSON output for production
        ],
        wrapper_class=structlog.make_filtering_bound_logger(logging.INFO),
        context_class=dict,
        logger_factory=structlog.PrintLoggerFactory(),
        cache_logger_on_first_use=True,
    )

    # Configure standard library logging
    logging.basicConfig(
        format="%(message)s",
        stream=sys.stdout,
        level=logging.INFO,
    )

