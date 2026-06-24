"""Tracing hooks.

This file intentionally avoids binding to one provider. Students can plug in LangSmith,
Langfuse, OpenTelemetry, or simple JSON traces.
"""

import logging
from collections.abc import Iterator
from contextlib import contextmanager
from time import perf_counter
from typing import Any


@contextmanager
def trace_span(name: str, attributes: dict[str, Any] | None = None) -> Iterator[dict[str, Any]]:
    """Minimal span context used by the skeleton.

    Grips duration, logs start and end events with metadata to standard logger.
    """
    logger = logging.getLogger("tracing")
    started = perf_counter()
    attributes = attributes or {}
    span: dict[str, Any] = {"name": name, "attributes": attributes, "duration_seconds": None}

    logger.info(f"▶▶▶ [SPAN START] {name} | Initial attributes: {attributes}")
    try:
        yield span
    except Exception as e:
        logger.error(f"❌❌❌ [SPAN ERROR] {name} failed: {e}")
        raise
    finally:
        duration = perf_counter() - started
        span["duration_seconds"] = duration
        logger.info(
            f"◀◀◀ [SPAN END] {name} completed in {duration:.4f}s | Final attributes: {span['attributes']}"
        )
