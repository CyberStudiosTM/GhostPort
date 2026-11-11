from __future__ import annotations

import time

import pytest

from ghostport.http_probe import check_json, is_json_media_type, probe_http


def test_json_response(http_server):
    r = probe_http("127.0.0.1", http_server, 2, expect_json=True)
    assert r.status == "ok"
    assert r.status_code == 200
    assert r.content_type.startswith("application/json")
    assert r.server == "ghost-test/1.0"
    assert r.response_time_ms is not None
    assert r.json_check.matched is True


def test_html_mismatch_is_not_conclusive(http_server):
    r = probe_http("127.0.0.1", http_server, 2, path="/html", expect_json=True)
    assert r.status == "ok"
    assert r.json_check.matched is False
    assert "does not identify the service" in r.json_check.message


def test_problem_json_and_missing_content_type(http_server):
    assert probe_http(
        "127.0.0.1", http_server, 2, path="/problem", expect_json=True
    ).json_check.matched
    none = probe_http("127.0.0.1", http_server, 2, path="/none", expect_json=True)
    assert none.json_check.matched is False
    assert none.content_type is None


def test_error_status_is_still_a_response(http_server):
    r = probe_http("127.0.0.1", http_server, 2, path="/missing")
    assert r.status == "ok"
    assert r.status_code == 404
    assert r.json_check is None


def test_redirects_not_followed(http_server):
    r = probe_http("127.0.0.1", http_server, 2, path="/redirect")
    assert r.status_code == 302


def test_timeout(http_server):
    started = time.perf_counter()
    r = probe_http("127.0.0.1", http_server, 0.3, path="/slow", expect_json=True)
    assert r.status == "timeout"
    assert time.perf_counter() - started < 2.5
    assert r.json_check.matched is None


def test_body_is_never_downloaded(http_server):
    started = time.perf_counter()
    r = probe_http("127.0.0.1", http_server, 2, path="/endless")
    assert r.status == "ok"
    assert time.perf_counter() - started < 2
    assert not hasattr(r, "body")


def test_non_http_service(raw_server):
    r = probe_http("127.0.0.1", raw_server, 2)
    assert r.status == "error"
    assert "valid HTTP" in r.error


def test_connection_failure(closed_port):
    r = probe_http("127.0.0.1", closed_port, 5)
    assert r.status == "error"


def test_trust_env_false(http_server, monkeypatch):
    monkeypatch.setenv("HTTP_PROXY", "http://127.0.0.1:9")
    monkeypatch.setenv("http_proxy", "http://127.0.0.1:9")
    monkeypatch.setenv("NO_PROXY", "")
    assert probe_http("127.0.0.1", http_server, 2).status == "ok"


def test_verbose_headers_redacted(http_server):
    r = probe_http("127.0.0.1", http_server, 2, verbose=True)
    headers = dict(r.headers)
    assert headers["set-cookie"] == "***"
    assert headers["x-api-key"] == "***"
    assert headers["server"] == "ghost-test/1.0"
    assert not probe_http("127.0.0.1", http_server, 2).headers


@pytest.mark.parametrize(
    ("ctype", "expected"),
    [
        ("application/json", True),
        ("Application/JSON; charset=utf-8", True),
        ("application/vnd.api+json", True),
        ("text/json", True),
        ("text/html", False),
        ("application/jsonp", False),
        (None, False),
        ("", False),
    ],
)
def test_media_type_matching(ctype, expected):
    assert check_json(ctype).matched is expected
    assert is_json_media_type(None) is False
