"""Best-effort listener identification. Never raises; never needs elevation."""

from __future__ import annotations

import ipaddress

import psutil

from ghostport.models import Listener, ProcessResult
from ghostport.redact import redact_cmdline, redact_path

_WILDCARDS = {"", "0.0.0.0", "::"}


def _is_local_bind(ip: str) -> bool:
    if ip in _WILDCARDS:
        return True
    try:
        addr = ipaddress.ip_address(ip.split("%", 1)[0])
    except ValueError:
        return False
    mapped = getattr(addr, "ipv4_mapped", None)
    return (mapped or addr).is_loopback


def _describe(pid: int, verbose: bool) -> Listener:
    name: str | None = None
    exe: str | None = None
    cmdline: tuple[str, ...] | None = None
    try:
        proc = psutil.Process(pid)
        try:
            name = proc.name()
        except (psutil.Error, OSError):
            name = None
        if verbose:
            try:
                exe = redact_path(proc.exe()) or None
            except (psutil.Error, OSError):
                exe = None
            try:
                cmdline = redact_cmdline(proc.cmdline()) or None
            except (psutil.Error, OSError):
                cmdline = None
    except (psutil.Error, OSError):
        pass
    return Listener(pid=pid, name=name, exe=exe, cmdline=cmdline)


def identify_process(port: int, verbose: bool = False) -> ProcessResult:
    try:
        connections = psutil.net_connections(kind="tcp")
    except psutil.AccessDenied:
        return ProcessResult(
            "unavailable", reason="permission denied reading the system socket table"
        )
    except (psutil.Error, OSError, NotImplementedError) as exc:
        return ProcessResult(
            "unavailable", reason=f"could not read the socket table ({type(exc).__name__})"
        )

    pids: list[int | None] = []
    for conn in connections:
        laddr = conn.laddr
        if (
            conn.status == psutil.CONN_LISTEN
            and laddr
            and laddr.port == port
            and _is_local_bind(laddr.ip)
            and conn.pid not in pids
        ):
            pids.append(conn.pid)

    if not pids:
        return ProcessResult(
            "not_found",
            reason="no listening socket found for this port (it may belong to a process "
            "this account cannot see, or have closed)",
        )

    visible = [pid for pid in pids if pid is not None]
    if not visible:
        return ProcessResult(
            "unavailable", reason="a listener exists but its owning PID is hidden by permissions"
        )

    listeners = tuple(_describe(pid, verbose) for pid in visible)
    primary = next((item for item in listeners if item.name), listeners[0])
    if primary.name:
        return ProcessResult("identified", pid=primary.pid, name=primary.name, listeners=listeners)
    return ProcessResult(
        "partial",
        pid=primary.pid,
        reason="process name is not readable with current permissions",
        listeners=listeners,
    )
