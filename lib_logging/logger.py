"""Structured logging for the Library Management System.

Outputs NDJSON (one JSON object per line) for easy analysis and ELK ingestion.
Uses only Python standard library.
"""

import json
import logging
import os
import sys
from datetime import datetime, timezone
from pathlib import Path


class StructuredFormatter(logging.Formatter):
    """Format log records as single-line JSON for ELK and analysis."""

    def format(self, record):
        log_obj = {
            "timestamp": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%f")[
                :-3
            ]
            + "Z",
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }
        if record.exc_info:
            log_obj["exception"] = self.formatException(record.exc_info)
        # Optional: add extra fields if present (e.g. from logger.info("msg", extra={...}))
        if hasattr(record, "extra_data") and isinstance(record.extra_data, dict):
            log_obj["data"] = record.extra_data
        return json.dumps(log_obj, ensure_ascii=False)


def get_logger(name: str) -> logging.Logger:
    """Return a logger with structured (NDJSON) output to file and console."""
    log_dir = Path(os.environ.get("LOG_DIR", "logs"))
    log_dir.mkdir(parents=True, exist_ok=True)
    log_file = log_dir / "library.log"

    logger = logging.getLogger(name)
    if logger.handlers:
        return logger

    logger.setLevel(logging.DEBUG)
    formatter = StructuredFormatter()

    # File handler: NDJSON for ELK / analysis
    fh = logging.FileHandler(log_file, encoding="utf-8")
    fh.setLevel(logging.DEBUG)
    fh.setFormatter(formatter)
    logger.addHandler(fh)

    # Console handler: same format for Docker/K8s stdout (captured by log shippers)
    ch = logging.StreamHandler(sys.stdout)
    ch.setLevel(logging.INFO)
    ch.setFormatter(formatter)
    logger.addHandler(ch)

    return logger
