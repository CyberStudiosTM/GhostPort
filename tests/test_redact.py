from __future__ import annotations

from ghostport.redact import redact_cmdline, redact_header, redact_text, redact_url


def test_sensitive_headers_masked():
    for name in ("Authorization", "Cookie", "Set-Cookie", "X-API-Key", "X-Auth-Token"):
        assert redact_header(name, "secret") == "***"
    assert redact_header("Server", "nginx") == "nginx"


def test_query_and_userinfo():
    assert redact_url("http://u:p@127.0.0.1:1/?token=abc&page=2") == (
        "http://***@127.0.0.1:1/?token=***&page=2"
    )
    assert redact_text("x?api_key=1&y=2") == "x?api_key=***&y=2"


def test_cmdline():
    out = redact_cmdline(["run", "--password", "hunter2", "SECRET=x", "--port=80", "--port", "81"])
    assert "hunter2" not in out and "SECRET=***" in out
    assert "--port=80" in out and "81" in out


def test_cmdline_capped_and_long_values_truncated():
    out = redact_cmdline([str(i) for i in range(50)])
    assert len(out) == 21 and out[-1] == "..."
    assert len(redact_header("X-Long", "a" * 1000)) <= 200
