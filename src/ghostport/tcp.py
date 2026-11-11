"""Localhost-only TCP connectivity probe."""

from __future__ import annotations

import socket
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Literal

from ghostport.models import TcpResult

LOOPBACK_ADDRESSES: tuple[str, ...] = ("127.0.0.1", "::1")

Outcome = tuple[Literal["open", "refused", "timeout", "error"], str, float, str | None]


def _family(address: str) -> socket.AddressFamily:
    return socket.AF_INET6 if ":" in address else socket.AF_INET


def _attempt(address: str, port: int, timeout: float) -> Outcome:
    sock: socket.socket | None = None
    started = time.perf_counter()
    try:
        sock = socket.socket(_family(address), socket.SOCK_STREAM)
        sock.settimeout(timeout)
        sock.connect((address, port))
    except ConnectionRefusedError:
        return ("refused", address, 0.0, None)
    except TimeoutError:
        return ("timeout", address, 0.0, None)
    except OSError as exc:
        # e.g. IPv6 loopback unavailable; only matters if nothing else answered.
        return ("error", address, 0.0, f"{address}: {exc.strerror or type(exc).__name__}")
    finally:
        if sock is not None:
            sock.close()
    return ("open", address, round((time.perf_counter() - started) * 1000, 2), None)


def probe_tcp(
    port: int,
    timeout: float,
    addresses: tuple[str, ...] = LOOPBACK_ADDRESSES,
) -> TcpResult:
    """Probe loopback addresses concurrently; the first successful connect wins.

    Only loopback addresses are ever contacted. Attempts run in parallel because
    Windows can take about two seconds to report a refused loopback connection.
    """
    outcomes: list[Outcome] = []
    pool = ThreadPoolExecutor(max_workers=len(addresses))
    try:
        futures = [pool.submit(_attempt, addr, port, timeout) for addr in addresses]
        for future in as_completed(futures):
            outcome = future.result()
            if outcome[0] == "open":
                return TcpResult("open", address=outcome[1], latency_ms=outcome[2])
            outcomes.append(outcome)
    finally:
        pool.shutdown(wait=False, cancel_futures=True)

    kinds = {o[0] for o in outcomes}
    if "timeout" in kinds:
        return TcpResult("timeout", error=f"no response within {timeout:g}s")
    if "refused" in kinds:
        return TcpResult("closed", error="connection refused")
    errors = [o[3] for o in outcomes if o[3]]
    return TcpResult("error", error=errors[0] if errors else "unable to connect")
