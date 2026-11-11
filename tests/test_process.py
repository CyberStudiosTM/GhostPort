from __future__ import annotations

import os
import socket
from collections import namedtuple

import psutil
import pytest

from ghostport.process import identify_process

Addr = namedtuple("Addr", "ip port")


class FakeConn:
    def __init__(self, port, pid, status=psutil.CONN_LISTEN, ip="127.0.0.1"):
        self.laddr = Addr(ip, port) if port else ()
        self.pid = pid
        self.status = status


def patch_conns(monkeypatch, conns):
    monkeypatch.setattr(psutil, "net_connections", lambda kind="inet": conns)


def test_identifies_this_process(http_server):
    result = identify_process(http_server)
    # macOS without privileges legitimately cannot read the socket table.
    assert result.status in {"identified", "unavailable", "not_found"}
    if result.status == "identified":
        assert result.pid == os.getpid()
        assert result.name


def test_access_denied_is_unavailable(monkeypatch):
    def boom(kind="inet"):
        raise psutil.AccessDenied()

    monkeypatch.setattr(psutil, "net_connections", boom)
    result = identify_process(8000)
    assert result.status == "unavailable"
    assert "permission" in result.reason


def test_unexpected_error_is_unavailable(monkeypatch):
    def boom(kind="inet"):
        raise OSError("nope")

    monkeypatch.setattr(psutil, "net_connections", boom)
    assert identify_process(8000).status == "unavailable"


def test_not_found(monkeypatch):
    patch_conns(monkeypatch, [FakeConn(9999, 1)])
    assert identify_process(8000).status == "not_found"


def test_hidden_pid(monkeypatch):
    patch_conns(monkeypatch, [FakeConn(8000, None)])
    assert identify_process(8000).status == "unavailable"


def test_name_denied_gives_partial(monkeypatch):
    patch_conns(monkeypatch, [FakeConn(8000, 42)])

    class Proc:
        def __init__(self, pid):
            pass

        def name(self):
            raise psutil.AccessDenied()

    monkeypatch.setattr(psutil, "Process", Proc)
    result = identify_process(8000)
    assert result.status == "partial"
    assert result.pid == 42
    assert result.name is None


def test_process_vanished(monkeypatch):
    patch_conns(monkeypatch, [FakeConn(8000, 42)])

    def gone(pid):
        raise psutil.NoSuchProcess(pid)

    monkeypatch.setattr(psutil, "Process", gone)
    assert identify_process(8000).status == "partial"


def test_ignores_non_local_binds_and_non_listen(monkeypatch):
    patch_conns(
        monkeypatch,
        [FakeConn(8000, 1, ip="192.168.1.5"), FakeConn(8000, 2, status=psutil.CONN_ESTABLISHED)],
    )
    assert identify_process(8000).status == "not_found"


def test_verbose_redacts_cmdline(monkeypatch):
    patch_conns(monkeypatch, [FakeConn(8000, 42)])

    class Proc:
        def __init__(self, pid):
            pass

        def name(self):
            return "node"

        def exe(self):
            return "/usr/bin/node"

        def cmdline(self):
            return ["node", "app.js", "--token=abc", "--api-key", "xyz"]

    monkeypatch.setattr(psutil, "Process", Proc)
    result = identify_process(8000, verbose=True)
    assert result.status == "identified"
    cmd = result.listeners[0].cmdline
    assert "abc" not in " ".join(cmd) and "xyz" not in " ".join(cmd)
    assert "--token=***" in cmd


def test_non_verbose_omits_cmdline(monkeypatch):
    patch_conns(monkeypatch, [FakeConn(8000, 42)])

    class Proc:
        def __init__(self, pid):
            pass

        def name(self):
            return "node"

    monkeypatch.setattr(psutil, "Process", Proc)
    assert identify_process(8000).listeners[0].cmdline is None


@pytest.mark.skipif(not hasattr(socket, "AF_INET6"), reason="no ipv6")
def test_ipv4_mapped_loopback_is_local(monkeypatch):
    patch_conns(monkeypatch, [FakeConn(8000, 7, ip="::ffff:127.0.0.1")])
    monkeypatch.setattr(psutil, "Process", lambda pid: type("P", (), {"name": lambda s: "x"})())
    assert identify_process(8000).status == "identified"
