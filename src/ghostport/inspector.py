"""Orchestrates the independent TCP, process, and HTTP checks."""

from __future__ import annotations

import platform
import sys
from typing import Any

import httpx
import psutil

from ghostport import __version__
from ghostport.http_probe import probe_http
from ghostport.models import (
    EXIT_CONNECTION_FAILED,
    EXIT_HTTP_CHECK_FAILED,
    EXIT_OK,
    HttpResult,
    InspectionResult,
)
from ghostport.process import identify_process
from ghostport.tcp import LOOPBACK_ADDRESSES, probe_tcp


def _diagnostics(timeout: float, path: str) -> dict[str, Any]:
    return {
        "ghostport": __version__,
        "python": platform.python_version(),
        "platform": sys.platform,
        "psutil": psutil.__version__,
        "httpx": httpx.__version__,
        "timeout_seconds": timeout,
        "loopback_addresses": list(LOOPBACK_ADDRESSES),
        "http": {
            "method": "GET",
            "path": path,
            "follow_redirects": False,
            "trust_env": False,
            "reads_body": False,
        },
    }


def inspect_port(
    port: int,
    *,
    timeout: float = 3.0,
    http: bool = False,
    expect_json: bool = False,
    path: str = "/",
    verbose: bool = False,
) -> InspectionResult:
    tcp = probe_tcp(port, timeout)
    # Process lookup is independent: its failure never changes the TCP verdict.
    process = identify_process(port, verbose=verbose)

    http_result: HttpResult | None = None
    if http:
        if tcp.connected and tcp.address:
            http_result = probe_http(
                tcp.address, port, timeout, path=path, expect_json=expect_json, verbose=verbose
            )
        else:
            http_result = HttpResult(status="skipped", error="TCP port is not open")

    if not tcp.connected:
        code = EXIT_CONNECTION_FAILED
    elif http_result is not None and (
        http_result.status != "ok"
        or (http_result.json_check is not None and http_result.json_check.matched is not True)
    ):
        code = EXIT_HTTP_CHECK_FAILED
    else:
        code = EXIT_OK

    return InspectionResult(
        port=port,
        tcp=tcp,
        process=process,
        http=http_result,
        exit_code=code,
        diagnostics=_diagnostics(timeout, path) if verbose else None,
    )
