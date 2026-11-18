from __future__ import annotations

import logging
import sys


def configure_logging(level: int = logging.INFO) -> None:
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(
        logging.Formatter(
            "%(asctime)s %(levelname)-8s %(name)s [%(message)s]",
            datefmt="%Y-%m-%dT%H:%M:%S",
        )
    )
    root = logging.getLogger()
    root.handlers.clear()
    root.addHandler(handler)
    root.setLevel(level)


def job_logger(name: str, job_id: str) -> logging.LoggerAdapter[logging.Logger]:
    return logging.LoggerAdapter(logging.getLogger(name), {"job_id": job_id})
