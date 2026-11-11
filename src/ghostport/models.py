"""Result types and the stable JSON schema (schema_version 1)."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Literal

from ghostport import __version__

SCHEMA_VERSION = 1
TOOL_NAME = "ghostport"

EXIT_OK = 0
EXIT_CONNECTION_FAILED = 1
EXIT_USAGE = 2
EXIT_HTTP_CHECK_FAILED = 3

TcpStatus = Literal["open", "closed", "timeout", "error"]
ProcessStatus = Literal["identified", "partial", "unavailable", "not_found"]
HttpStatus = Literal["ok", "error", "timeout", "skipped"]


@dataclass(frozen=True)
class TcpResult:
    status: TcpStatus
    address: str | None = None
    latency_ms: float | None = None
    error: str | None = None

    @property
    def connected(self) -> bool:
        return self.status == "open"

    def to_dict(self) -> dict[str, Any]:
        return {
            "status": self.status,
            "connected": self.connected,
            "address": self.address,
            "latency_ms": self.latency_ms,
            "error": self.error,
        }


@dataclass(frozen=True)
class Listener:
    pid: int | None
    name: str | None = None
    exe: str | None = None
    cmdline: tuple[str, ...] | None = None

    def to_dict(self, verbose: bool) -> dict[str, Any]:
        data: dict[str, Any] = {"pid": self.pid, "name": self.name}
        if verbose:
            data["exe"] = self.exe
            data["cmdline"] = list(self.cmdline) if self.cmdline is not None else None
        return data


@dataclass(frozen=True)
class ProcessResult:
    status: ProcessStatus
    pid: int | None = None
    name: str | None = None
    reason: str | None = None
    listeners: tuple[Listener, ...] = ()

    def to_dict(self, verbose: bool) -> dict[str, Any]:
        return {
            "status": self.status,
            "pid": self.pid,
            "name": self.name,
            "reason": self.reason,
            "listeners": [item.to_dict(verbose) for item in self.listeners],
        }


@dataclass(frozen=True)
class JsonCheck:
    matched: bool | None
    media_type: str | None
    message: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "expected": True,
            "matched": self.matched,
            "media_type": self.media_type,
            "message": self.message,
        }


@dataclass(frozen=True)
class HttpResult:
    status: HttpStatus
    url: str | None = None
    status_code: int | None = None
    content_type: str | None = None
    server: str | None = None
    response_time_ms: float | None = None
    error: str | None = None
    json_check: JsonCheck | None = None
    headers: tuple[tuple[str, str], ...] = field(default=())

    def to_dict(self, verbose: bool) -> dict[str, Any]:
        data: dict[str, Any] = {
            "status": self.status,
            "url": self.url,
            "status_code": self.status_code,
            "content_type": self.content_type,
            "server": self.server,
            "response_time_ms": self.response_time_ms,
            "error": self.error,
            "json_check": self.json_check.to_dict() if self.json_check else None,
        }
        if verbose:
            data["headers"] = [{"name": n, "value": v} for n, v in self.headers]
        return data


@dataclass(frozen=True)
class InspectionResult:
    port: int
    tcp: TcpResult
    process: ProcessResult
    http: HttpResult | None
    exit_code: int
    diagnostics: dict[str, Any] | None = None

    def to_dict(self, verbose: bool = False) -> dict[str, Any]:
        data: dict[str, Any] = {
            "schema_version": SCHEMA_VERSION,
            "tool": TOOL_NAME,
            "version": __version__,
            "ok": self.exit_code == EXIT_OK,
            "exit_code": self.exit_code,
            "target": {"host": "localhost", "port": self.port},
            "tcp": self.tcp.to_dict(),
            "process": self.process.to_dict(verbose),
            "http": self.http.to_dict(verbose) if self.http else None,
        }
        if verbose:
            data["diagnostics"] = self.diagnostics
        return data


def error_envelope(code: str, message: str, exit_code: int = EXIT_USAGE) -> dict[str, Any]:
    return {
        "schema_version": SCHEMA_VERSION,
        "tool": TOOL_NAME,
        "version": __version__,
        "ok": False,
        "exit_code": exit_code,
        "error": {"code": code, "message": message},
    }
