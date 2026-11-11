from __future__ import annotations

import json

import psutil
import pytest
from typer.testing import CliRunner

from ghostport.cli import app

runner = CliRunner()

TOP_KEYS = {
    "schema_version",
    "tool",
    "version",
    "ok",
    "exit_code",
    "target",
    "tcp",
    "process",
    "http",
}
TCP_KEYS = {"status", "connected", "address", "latency_ms", "error"}
PROC_KEYS = {"status", "pid", "name", "reason", "listeners"}
HTTP_KEYS = {
    "status",
    "url",
    "status_code",
    "content_type",
    "server",
    "response_time_ms",
    "error",
    "json_check",
}


def run_json(*args):
    result = runner.invoke(app, ["inspect", *args, "--json"])
    return result.exit_code, json.loads(result.stdout)


def test_open_port_schema(http_server):
    code, data = run_json(str(http_server))
    assert code == 0
    assert set(data) == TOP_KEYS
    assert data["schema_version"] == 1
    assert set(data["tcp"]) == TCP_KEYS
    assert set(data["process"]) == PROC_KEYS
    assert data["http"] is None
    assert data["ok"] is True and data["exit_code"] == 0
    assert data["target"] == {"host": "localhost", "port": http_server}


def test_http_schema_and_json_check(http_server):
    code, data = run_json(str(http_server), "--http", "--expect-json")
    assert code == 0
    assert set(data["http"]) == HTTP_KEYS
    assert data["http"]["json_check"]["matched"] is True
    assert data["http"]["status_code"] == 200


def test_json_mismatch_exit_3(http_server):
    code, data = run_json(str(http_server), "--http", "--expect-json", "--path", "/html")
    assert code == 3
    assert data["ok"] is False and data["exit_code"] == 3
    assert data["http"]["json_check"]["matched"] is False
    assert data["tcp"]["connected"] is True


def test_non_http_exit_3(raw_server):
    code, data = run_json(str(raw_server), "--http")
    assert code == 3
    assert data["http"]["status"] == "error"


def test_closed_port_exit_1(closed_port):
    code, data = run_json(str(closed_port), "--http")
    assert code == 1
    assert data["tcp"]["status"] == "closed"
    assert data["http"]["status"] == "skipped"
    assert set(data) == TOP_KEYS


@pytest.mark.parametrize("bad", ["0", "65536", "-1", "abc", "80.5", ""])
def test_invalid_port_json(bad):
    result = runner.invoke(app, ["inspect", "--json", "--", bad])
    assert result.exit_code == 2
    data = json.loads(result.stdout)
    assert data["error"]["code"] == "invalid_port"
    assert data["ok"] is False and data["exit_code"] == 2


def test_invalid_port_text():
    result = runner.invoke(app, ["inspect", "99999"])
    assert result.exit_code == 2
    assert "invalid port" in result.output


@pytest.mark.parametrize(
    "args",
    [["--timeout", "0"], ["--timeout", "999"], ["--expect-json"], ["--http", "--path", "x"]],
)
def test_usage_errors(args, http_server):
    result = runner.invoke(app, ["inspect", str(http_server), *args, "--json"])
    assert result.exit_code == 2
    assert json.loads(result.stdout)["ok"] is False


def test_process_failure_does_not_invalidate_tcp(http_server, monkeypatch):
    def boom(kind="inet"):
        raise psutil.AccessDenied()

    monkeypatch.setattr(psutil, "net_connections", boom)
    code, data = run_json(str(http_server), "--http")
    assert code == 0
    assert data["tcp"]["status"] == "open"
    assert data["process"]["status"] == "unavailable"
    assert data["http"]["status"] == "ok"


def test_verbose_json_redacts(http_server):
    code, data = run_json(str(http_server), "--http", "--verbose")
    assert code == 0
    assert "diagnostics" in data
    assert data["diagnostics"]["http"]["reads_body"] is False
    headers = {h["name"]: h["value"] for h in data["http"]["headers"]}
    assert headers["set-cookie"] == "***"
    text = json.dumps(data)
    assert "supersecret" not in text and "topsecret" not in text


def test_terminal_output(http_server):
    result = runner.invoke(app, ["inspect", str(http_server), "--http", "--expect-json", "-v"])
    assert result.exit_code == 0
    for needle in ("TCP", "PROCESS", "HTTP", "JSON", "200", "ghost-test/1.0"):
        assert needle in result.output
    assert "supersecret" not in result.output


def test_terminal_closed(closed_port):
    result = runner.invoke(app, ["inspect", str(closed_port)])
    assert result.exit_code == 1
    assert "closed" in result.output


def test_version_and_help():
    assert "ghostport" in runner.invoke(app, ["--version"]).output
    assert "inspect" in runner.invoke(app, ["--help"]).output
