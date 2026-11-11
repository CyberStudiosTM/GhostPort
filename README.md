# GhostPort

A tiny forensic CLI for local TCP ports. Ask one question of `localhost`: *what is answering on this port, and does it behave the way I expect?*

A CyberStudios tool. Standalone: no dependency on any other CyberStudios project.

```
$ ghostport inspect 8765 --http --expect-json
+- ghostport v0.1.0  localhost:8765 ------------------------------------------+
|                                                                             |
|  TCP      [+] open on 127.0.0.1  1.11 ms                                    |
|  PROCESS  [+] python.exe  pid 17724                                         |
|  HTTP     [+] 200  text/html; charset=utf-8  403.44 ms  server:             |
|           SimpleHTTP/0.6 Python/3.11.9                                      |
|  JSON     [x] Content-Type 'text/html' is not a JSON media type; this       |
|           alone does not identify the service                               |
|                                                                             |
|  Port is open, but the HTTP check did not pass. This does not identify the  |
|  service.                                                                   |
|                                                                             |
+-----------------------------------------------------------------------------+
```

In a real terminal the panel uses rounded borders and a pastel palette (lavender, mint, sky, pink). `NO_COLOR` is respected.

## Install

Requires Python 3.11+.

```
pip install git+https://github.com/CyberStudiosTM/GhostPort.git
```

Or from a checkout:

```
pip install -e ".[dev]"
```

## Usage

```
ghostport inspect PORT [--http] [--expect-json] [--json] [--verbose]
                       [--timeout SECONDS] [--path /PATH]
```

| Option | Meaning |
| --- | --- |
| `--http` | One bounded `GET` (headers only). Reports status, content type, response time, `Server`. |
| `--expect-json` | Check that `Content-Type` is `application/json`, `text/json`, or `*+json`. Requires `--http`. |
| `--json` | Stable machine-readable output (schema below). |
| `--verbose`, `-v` | Extra diagnostics, with sensitive values redacted. |
| `--timeout`, `-t` | Per-operation timeout, 0.05 to 30 seconds. Default 3. |
| `--path` | Request path for `--http`. Default `/`. |

Examples:

```
ghostport inspect 3000
ghostport inspect 8080 --http
ghostport inspect 8000 --http --expect-json --json
ghostport inspect 5432 --verbose
```

### Exit codes

| Code | Meaning |
| --- | --- |
| 0 | Port accepted a connection, and any requested HTTP checks passed. |
| 1 | Nothing accepted a localhost connection (closed, timeout, or error). |
| 2 | Invalid input: bad port, timeout, path, or option combination. |
| 3 | Port is open, but the HTTP probe failed or `--expect-json` did not match. |

An HTTP error status such as 404 or 500 is still a response and exits 0. Failing to identify the owning process never changes the exit code.

### JSON schema (`schema_version: 1`)

TCP, process, and HTTP results are independent sections. Keys are always present; unavailable values are `null`.

```json
{
  "schema_version": 1,
  "tool": "ghostport",
  "version": "0.1.0",
  "ok": true,
  "exit_code": 0,
  "target": { "host": "localhost", "port": 8765 },
  "tcp": { "status": "open", "connected": true, "address": "127.0.0.1", "latency_ms": 2.7, "error": null },
  "process": { "status": "identified", "pid": 17724, "name": "python.exe", "reason": null, "listeners": [] },
  "http": null
}
```

- `tcp.status`: `open | closed | timeout | error`
- `process.status`: `identified | partial | unavailable | not_found`
- `http`: `null` unless `--http`. Otherwise `status` is `ok | error | timeout | skipped`, with `url`, `status_code`, `content_type`, `server`, `response_time_ms`, `error`, and `json_check` (`null`, or `{expected, matched, media_type, message}`).
- `--verbose` adds `diagnostics`, per-listener `exe`/`cmdline`, and `http.headers`.
- Invalid input prints `{schema_version, tool, version, ok: false, exit_code: 2, error: {code, message}}`.

Additive changes keep `schema_version` at 1; breaking changes bump it.

## Safety model

- Contacts only `127.0.0.1` and `::1`. No host option, no scanning.
- Read-only. Never kills, signals, or modifies processes. No administrator rights needed.
- HTTP: one `GET`, no redirects followed, response body never read or shown, `trust_env=False` so proxy environment variables cannot interfere.
- No telemetry, no external services.
- `--verbose` masks sensitive header values (cookies, auth, tokens, keys), URL credentials, sensitive query values, and sensitive command-line arguments.

## Limitations

- Process identification depends on OS permissions. On macOS reading the socket table usually needs elevation; GhostPort reports "unavailable" and carries on. On Windows, system processes may show a PID without a name.
- A closed loopback port can take about 2 seconds to report on Windows. Keep `--timeout` at 3 or higher there.
- `--timeout` applies per network operation, not as a hard total deadline.
- A JSON content type is a hint, not an identification. GhostPort never claims to identify a service conclusively.
- TLS-only services will fail the plain HTTP probe (reported as not valid HTTP).
- IPv4 and IPv6 loopback are checked; other interfaces are out of scope.

## Development

```
pip install -e ".[dev]"
ruff check .
ruff format --check .
python -m pytest
```

CI runs on Windows, Linux, and macOS (Python 3.11 to 3.13).

## License

MIT. See [LICENSE](LICENSE).
