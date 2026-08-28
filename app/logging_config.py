from __future__ import annotations

import logging
import os
import sys
import uuid
from contextvars import ContextVar
from datetime import datetime, timezone
from typing import Any

try:
    import structlog
except Exception:
    structlog = None  # type: ignore[assignment]


_TRACE_ID: ContextVar[str] = ContextVar("trace_id", default="")


def configure_langsmith_tracing() -> None:
    """Enable LangSmith tracing through LangChain environment variables."""
    os.environ.setdefault("LANGCHAIN_TRACING_V2", "true")
    os.environ.setdefault("LANGSMITH_TRACING", "true")


def new_trace_id() -> str:
    """Create a unique trace identifier for one agent execution."""
    return uuid.uuid4().hex


def set_trace_id(trace_id: str | None = None) -> str:
    """Bind a trace identifier to the current context."""
    value = trace_id or new_trace_id()
    _TRACE_ID.set(value)
    if structlog is not None:
        structlog.contextvars.clear_contextvars()
        structlog.contextvars.bind_contextvars(trace_id=value)
    return value


def get_trace_id() -> str:
    """Return the current trace identifier, creating one if needed."""
    return _TRACE_ID.get() or set_trace_id()


def _add_trace_id(_: Any, __: str, event_dict: dict[str, Any]) -> dict[str, Any]:
    event_dict.setdefault("trace_id", get_trace_id())
    return event_dict


def configure_logging() -> None:
    """Configure JSON logs for graph nodes and support code."""
    configure_langsmith_tracing()
    logging.basicConfig(format="%(message)s", stream=sys.stdout, level=logging.INFO, force=True)
    if structlog is None:
        return
    structlog.configure(
        processors=[
            structlog.contextvars.merge_contextvars,
            _add_trace_id,
            structlog.processors.TimeStamper(fmt="iso", key="timestamp", utc=True),
            structlog.processors.add_log_level,
            structlog.processors.JSONRenderer(),
        ],
        wrapper_class=structlog.make_filtering_bound_logger(logging.INFO),
        logger_factory=structlog.PrintLoggerFactory(file=sys.stdout),
        cache_logger_on_first_use=True,
    )


def get_logger() -> Any:
    """Return the configured structured logger."""
    configure_langsmith_tracing()
    if structlog is not None:
        return structlog.get_logger()
    return _FallbackJsonLogger()


class _FallbackJsonLogger:
    def __init__(self, **context: Any) -> None:
        self.context = context

    def bind(self, **context: Any) -> "_FallbackJsonLogger":
        return _FallbackJsonLogger(**{**self.context, **context})

    def info(self, event: str, **fields: Any) -> None:
        self._emit("info", event, fields)

    def exception(self, event: str, **fields: Any) -> None:
        self._emit("error", event, fields)

    def _emit(self, level: str, event: str, fields: dict[str, Any]) -> None:
        import json

        payload = {
            "event": event,
            "level": level,
            "trace_id": get_trace_id(),
            "timestamp": datetime.now(timezone.utc).isoformat(),
            **self.context,
            **fields,
        }
        print(json.dumps(payload, ensure_ascii=False), file=sys.stdout)
