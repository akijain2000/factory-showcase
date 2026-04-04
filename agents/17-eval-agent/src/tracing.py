"""Lightweight OTEL-shaped tracing (Protocol); no OpenTelemetry SDK."""
from __future__ import annotations
import functools, json, logging, os, threading, time, uuid
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable, Dict, Optional, Protocol, TypeVar, runtime_checkable

F = TypeVar("F", bound=Callable[..., Any])
SERVICE_NAME = "17-eval-agent"


class ExportKind(str, Enum):
    NONE, CONSOLE, OTLP = "none", "console", "otlp"


@runtime_checkable
class SpanExporter(Protocol):
    def export(self, span: "FinishedSpan") -> None: ...


@dataclass
class FinishedSpan:
    name: str
    trace_id: str
    span_id: str
    parent_span_id: Optional[str]
    start_ns: int
    end_ns: int
    attrs: Dict[str, Any] = field(default_factory=dict)


@dataclass
class SpanContext:
    trace_id: str
    span_id: str
    parent_span_id: Optional[str] = None


_tls = threading.local()


def current_context() -> Optional[SpanContext]:
    return getattr(_tls, "ctx", None)


def attach_context(ctx: SpanContext) -> None:
    _tls.ctx = ctx


def detach_context() -> None:
    if hasattr(_tls, "ctx"):
        delattr(_tls, "ctx")


def inject_carrier() -> Dict[str, str]:
    c = current_context()
    return {"traceparent": f"00-{c.trace_id}-{c.span_id}-01"} if c else {}


def extract_carrier(h: Dict[str, str]) -> Optional[SpanContext]:
    p = (h.get("traceparent") or "").split("-")
    return SpanContext(p[1], p[2][:16]) if len(p) >= 3 and p[0] == "00" else None


class ConsoleExporter:
    def export(self, s: FinishedSpan) -> None:
        ms = round((s.end_ns - s.start_ns) / 1e6, 3)
        d = {"service": SERVICE_NAME, "span": s.name, "trace_id": s.trace_id, "span_id": s.span_id, "parent": s.parent_span_id, "duration_ms": ms}
        d.update(s.attrs)
        print(json.dumps(d))


class NoOpExporter:
    def export(self, s: FinishedSpan) -> None:
        pass


class OtlpExporter:
    def export(self, s: FinishedSpan) -> None:
        logging.getLogger(__name__).debug("otlp.stub %s", s.name)


@dataclass
class TracerProvider:
    exporter: SpanExporter = field(default_factory=NoOpExporter)

    def set_exporter_kind(self, k: ExportKind) -> None:
        self.exporter = {ExportKind.CONSOLE: ConsoleExporter(), ExportKind.OTLP: OtlpExporter(), ExportKind.NONE: NoOpExporter()}[k]


_provider = TracerProvider()


def get_tracer_provider() -> TracerProvider:
    return _provider


def configure_from_env() -> None:
    k = os.environ.get("TRACE_EXPORTER", "none").lower()
    _provider.set_exporter_kind({"console": ExportKind.CONSOLE, "otlp": ExportKind.OTLP}.get(k, ExportKind.NONE))


class Span:
    def __init__(self, name: str, provider: Optional[TracerProvider] = None) -> None:
        self.name, self.provider = name, provider or _provider
        par = current_context()
        self.trace_id, self.span_id = (par.trace_id if par else uuid.uuid4().hex), uuid.uuid4().hex[:16]
        self.parent_span_id = par.span_id if par else None
        self._attrs, self._t0, self._prev = {}, 0, None

    def set_attribute(self, key: str, value: Any) -> None:
        self._attrs[key] = value

    def __enter__(self) -> Span:
        self._t0, self._prev = time.time_ns(), current_context()
        attach_context(SpanContext(self.trace_id, self.span_id, self.parent_span_id))
        return self

    def __exit__(self, *exc: Any) -> None:
        attach_context(self._prev) if self._prev is not None else detach_context()
        self.provider.exporter.export(FinishedSpan(self.name, self.trace_id, self.span_id, self.parent_span_id, self._t0, time.time_ns(), dict(self._attrs)))


def cost_tracked(price_per_1k_input: float = 0.0, price_per_1k_output: float = 0.0) -> Callable[[F], F]:
    def deco(fn: F) -> F:
        @functools.wraps(fn)
        def wrapper(*a: Any, **kw: Any) -> Any:
            with Span(f"tool:{fn.__name__}") as sp:
                out = fn(*a, **kw)
                u = (out or {}).get("usage") if isinstance(out, dict) else None
                tin, tout = 0, 0
                if isinstance(u, dict):
                    tin = int(u.get("prompt_tokens") or u.get("input_tokens") or 0)
                    tout = int(u.get("completion_tokens") or u.get("output_tokens") or 0)
                sp.set_attribute("tokens.input", tin)
                sp.set_attribute("tokens.output", tout)
                sp.set_attribute("cost.usd", round(tin / 1e3 * price_per_1k_input + tout / 1e3 * price_per_1k_output, 6))
                return out

        return wrapper  # type: ignore[return-value]

    return deco


class TraceJsonFormatter(logging.Formatter):
    def format(self, r: logging.LogRecord) -> str:
        c = current_context()
        return json.dumps({"ts": self.formatTime(r, self.datefmt), "level": r.levelname, "logger": r.name, "msg": r.getMessage(), "trace_id": c.trace_id if c else "", "span_id": c.span_id if c else "", "service": SERVICE_NAME})
