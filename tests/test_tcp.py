from __future__ import annotations

import socket

from ghostport.tcp import probe_tcp


def test_open_port(http_server):
    result = probe_tcp(http_server, timeout=2)
    assert result.status == "open"
    assert result.connected
    assert result.address == "127.0.0.1"
    assert result.latency_ms is not None


def test_closed_port(closed_port):
    result = probe_tcp(closed_port, timeout=5)
    assert result.status == "closed"
    assert not result.connected


def test_timeout(monkeypatch):
    class Slow(socket.socket):
        def connect(self, address):
            raise TimeoutError

    monkeypatch.setattr("ghostport.tcp.socket.socket", Slow)
    assert probe_tcp(1234, timeout=0.1).status == "timeout"


def test_other_os_error_reported(monkeypatch):
    class Broken(socket.socket):
        def connect(self, address):
            raise OSError(10013, "access denied")

    monkeypatch.setattr("ghostport.tcp.socket.socket", Broken)
    result = probe_tcp(1234, timeout=0.1)
    assert result.status == "error"
    assert result.error


def test_ipv6_unavailable_does_not_mask_refused(monkeypatch, closed_port):
    real = socket.socket

    class NoV6(real):
        def __init__(self, family=socket.AF_INET, *a, **k):
            if family == socket.AF_INET6:
                raise OSError("address family not supported")
            super().__init__(family, *a, **k)

    # Constructor failure for IPv6 must not crash the probe.
    monkeypatch.setattr("ghostport.tcp.socket.socket", NoV6)
    try:
        result = probe_tcp(closed_port, timeout=5)
    except OSError:
        result = None
    assert result is not None and result.status == "closed"
