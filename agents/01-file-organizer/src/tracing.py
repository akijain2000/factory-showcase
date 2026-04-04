"""OTel-style tracing (Protocol exporters, no OTEL SDK): provider, propagation, tool-cost spans, JSON logs."""
from __future__ import annotations

import functools
import json
import logging
import secrets
import time
from contextlib import contextmanager
from contextvars import ContextVar
from dataclasses import dataclass
from typing import Any, Callable, Dict, Iterator, Literal, Optional, Protocol, TypeVar

ExporterKind = Literal["console", "otlp", "none"]
_span_ctx: ContextVar[Optional["SpanContext"]] = ContextVar("trace_span", default=None)


@dataclass(frozen=True)
class SpanContext:
    trace_id: str
    span_id: str
    parent_span_id: Optional[str] = None


class SpanExporter(Protocol):
    def export(self, name: str, start_ns: int, end_ns: int, attrs: Dict[str, Any]) -> None: ...


class _CallableExporter:
    __slots__ = ("_f",)

    def __init__(self, f: Callable[[str, int, int, Dict[str, Any]], None]) -> None:
        self._f = f

    def export(self, name: str, start_ns: int, end_ns: int, attrs: Dict[str, Any]) -> None:
        self._f(name, start_ns, end_ns, attrs)


class TracerProvider:
    def __init__(self, exporter: ExporterKind = "none", *, otlp_endpoint: str = "http://localhost:4318/v1/traces") -> None:
        def _c(n: str, t0: int, t1: int, a: Dict[str, Any]) -> None:
            print(json.dumps({"span": n, "start_ns": t0, "end_ns": t1, **a}, default=str))

        def _o(n: str, t0: int, t1: int, a: Dict[str, Any]) -> None:
            logging.getLogger("tracing.otlp").debug("POST %s span=%s dur_ns=%s", otlp_endpoint, n, t1 - t0)

        fn: Callable[[str, int, int, Dict[str, Any]], None] = (
            _c if exporter == "console" else _o if exporter == "otlp" else lambda _n, _t0, _t1, _a: None
        )
        self._ex: SpanExporter = _CallableExporter(fn)

    def export_span(self, name: str, start_ns: int, end_ns: int, attrs: Optional[Dict[str, Any]] = None) -> None:
        m = dict(attrs or {})
        c = _span_ctx.get()
        if c:
            m.setdefault("trace_id", c.trace_id)
            m.setdefault("span_id", c.span_id)
        self._ex.export(name, start_ns, end_ns, m)


def new_root_span() -> SpanContext:
    return SpanContext(secrets.token_hex(16), secrets.token_hex(8))


def start_child_span(parent: SpanContext) -> SpanContext:
    return SpanContext(parent.trace_id, secrets.token_hex(8), parent.span_id)


def inject_context(ctx: SpanContext) -> Dict[str, str]:
    return {"traceparent": f"00-{ctx.trace_id}-{ctx.span_id}-01"}


def extract_context(carrier: Dict[str, str]) -> Optional[SpanContext]:
    p = (carrier.get("traceparent") or "").split("-")
    return SpanContext(p[1], p[2]) if len(p) >= 4 and p[0] == "00" else None


@contextmanager
def active_span(ctx: SpanContext) -> Iterator[SpanContext]:
    tok = _span_ctx.set(ctx)
    try:
        yield ctx
    finally:
        _span_ctx.reset(tok)


F = TypeVar("F", bound=Callable[..., Any])


def track_tool_cost(
    provider: TracerProvider, usage_from_result: Callable[[Any], tuple[int, int, float]] | None = None
) -> Callable[[F], F]:
    def _usage(res: Any) -> tuple[int, int, float]:
        if usage_from_result:
            return usage_from_result(res)
        if isinstance(res, dict):
            u = res.get("usage") or {}
            return int(u.get("input_tokens", 0)), int(u.get("output_tokens", 0)), float(u.get("cost_usd", 0.0))
        return (0, 0, 0.0)

    def deco(fn: F) -> F:
        @functools.wraps(fn)
        def w(*a: Any, **k: Any) -> Any:
            t0 = time.time_ns()
            out = fn(*a, **k)
            i, o, c = _usage(out)
            provider.export_span(f"tool:{fn.__name__}", t0, time.time_ns(), {"tool": fn.__name__, "input_tokens": i, "output_tokens": o, "cost_usd": c})
            return out

        return w  # type: ignore[return-value]

    return deco


class StructuredTraceFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        c = _span_ctx.get()
        d = {"ts": self.formatTime(record, self.datefmt), "level": record.levelname, "logger": record.name, "message": record.getMessage(), "trace_id": c.trace_id if c else None, "span_id": c.span_id if c else None}
        return json.dumps(d, default=str)
