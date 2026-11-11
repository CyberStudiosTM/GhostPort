# 👻 GhostPort

<div align="center">

**A little ghost in your localhost.**

*Find out what's listening, who's behind it, and whether it's answering the way you expected.*

**A CyberStudios™ developer utility**

![Python](https://img.shields.io/badge/Python-3.11%2B-BDA9F2?style=flat-square)
![Platform](https://img.shields.io/badge/Platform-Windows%20%7C%20Linux%20%7C%20macOS-A9E8DC?style=flat-square)
![License](https://img.shields.io/badge/License-MIT-B9DDF6?style=flat-square)
![Version](https://img.shields.io/badge/Version-0.1.0-F4C7E8?style=flat-square)

[Getting Started](#-getting-started) · [Commands](#-commands) · [How It Works](#-how-it-works) · [Safety](#-safety--privacy) · [Contributing](CONTRIBUTING.md)

</div>

---

## ✦ Welcome to GhostPort

Somewhere inside your computer, a service is listening.

Maybe it's your development server. Maybe it's an MCP endpoint. Maybe something else has occupied the port you expected to use.

**GhostPort helps you investigate.**

It's a lightweight, local-first command-line utility that inspects TCP ports on your own machine, identifies listening processes when possible, and checks how local HTTP services respond.

No dashboards. No cloud account. No background daemon.

Just you, your terminal, and a little ghost with questions.

### What can it do?

- **Inspect local ports.** Check whether a TCP port accepts connections.
- **Identify processes.** Find the associated PID and process name when the operating system permits.
- **Probe HTTP services.** Inspect status codes, content types, server headers, and response times.
- **Check JSON expectations.** Find out when a service isn't returning the expected JSON media type.
- **Generate structured reports.** Use machine-readable JSON output in scripts and developer workflows.
- **Keep diagnostics private.** No telemetry, external requests, or process termination.

GhostPort is an independent CyberStudios™ project. It does not require CyberCore or any other CyberStudios software.

---

## 🌱 Getting Started

**Requirements:** Python 3.11 or newer.

### Install from PyPI

```bash
python -m pip install ghostport-cli
```

The PyPI package is named `ghostport-cli`; the command and import name are `ghostport`.

### Install from GitHub

```bash
python -m pip install git+https://github.com/CyberStudiosTM/GhostPort.git
```

### Install for development

```bash
git clone https://github.com/CyberStudiosTM/GhostPort.git
cd GhostPort
python -m pip install -e ".[dev]"
```

### Your first inspection

```bash
ghostport inspect 8080
```

Check the HTTP response:

```bash
ghostport inspect 8080 --http
```

Expect a JSON response:

```bash
ghostport inspect 8080 --http --expect-json
```

Export a report:

```bash
ghostport inspect 8080 --json
```

> **Note:** A successful connection doesn't prove which service owns a port. GhostPort reports the evidence it can observe without inventing an identity.

---

## 🖥️ Commands

```text
ghostport inspect PORT [--http] [--expect-json] [--json] [--verbose]
                       [--timeout SECONDS] [--path /PATH]
```

| Option | Description |
|---|---|
| `--http` | Send one bounded HTTP GET request and inspect response headers. |
| `--expect-json` | Validate that the HTTP content type is a supported JSON media type. Requires `--http`. |
| `--json` | Return structured, machine-readable output. |
| `--verbose`, `-v` | Display additional diagnostics with sensitive values redacted. |
| `--timeout`, `-t` | Set the per-operation timeout from 0.05 to 30 seconds. Default: 3 seconds. |
| `--path` | Specify the HTTP request path. Default: `/`. |

### Example investigations

**Is my development server listening?**

```bash
ghostport inspect 3000
```

**What's responding on my API port?**

```bash
ghostport inspect 8000 --http
```

**Is this endpoint returning JSON?**

```bash
ghostport inspect 8000 --http --expect-json
```

**I need a report for another tool.**

```bash
ghostport inspect 8000 --http --json
```

**Show additional diagnostics.**

```bash
ghostport inspect 5432 --verbose
```

---

## ✧ Example Output

This example comes from a local GhostPort test against a Python HTTP server.

```text
$ ghostport inspect 8765 --http --expect-json

ghostport v0.1.0 · localhost:8765

TCP       [+] open on 127.0.0.1 · 1.11 ms
PROCESS   [+] python.exe · pid 17724
HTTP      [+] 200 · text/html; charset=utf-8
              403.44 ms · SimpleHTTP/0.6 Python/3.11.9
JSON      [x] Content-Type is not a JSON media type

Port is open, but the HTTP check did not pass.
This does not identify the service.
```

The actual terminal interface uses rounded panels and a pastel color palette. GhostPort also respects `NO_COLOR`.

---

## 🔎 How It Works

GhostPort separates its diagnostics into three independent stages.

### 01 / TCP inspection

Attempts a connection to the requested port using IPv4 and IPv6 loopback addresses.

Reports whether the connection succeeds, fails, or times out.

### 02 / Process inspection

Attempts to identify the listening process using available operating-system information.

Process identification may be unavailable due to permissions or platform limitations. That does not change the TCP result.

### 03 / HTTP inspection

When requested, sends a single HTTP GET request and inspects the response headers.

GhostPort does not read or display the response body, follow redirects, or infer a service's identity from its content type.

---

## 📡 JSON Reports

GhostPort provides a stable, versioned JSON report format.

```json
{
  "schema_version": 1,
  "tool": "ghostport",
  "version": "0.1.0",
  "ok": true,
  "exit_code": 0,
  "target": {
    "host": "localhost",
    "port": 8765
  },
  "tcp": {
    "status": "open",
    "connected": true,
    "address": "127.0.0.1",
    "latency_ms": 2.7,
    "error": null
  },
  "process": {
    "status": "identified",
    "pid": 17724,
    "name": "python.exe",
    "reason": null,
    "listeners": []
  },
  "http": null
}
```

The `tcp`, `process`, and `http` sections remain independent. Unavailable values are represented as `null`.

Supported status values:

- TCP: `open`, `closed`, `timeout`, `error`
- Process: `identified`, `partial`, `unavailable`, `not_found`
- HTTP: `ok`, `error`, `timeout`, `skipped`

When `--http` is enabled, the HTTP section includes the URL, status code, content type, server, response time, error information, and optional JSON validation result.

Verbose output may additionally include redacted diagnostics, listener details, and HTTP headers.

Invalid input returns a JSON error object containing the schema version, tool name, version, failure status, exit code, and structured error.

Additive schema changes preserve `schema_version: 1`. Breaking changes require a new schema version.

---

## 🚦 Exit Codes

| Code | Meaning |
|---|---|
| `0` | TCP connection succeeded and requested HTTP checks passed. |
| `1` | TCP connection failed, timed out, or encountered an error. |
| `2` | Invalid arguments or unsupported option combinations. |
| `3` | TCP succeeded, but the requested HTTP or JSON check failed. |

HTTP status codes such as `404` or `500` still count as valid HTTP responses for exit-code purposes.

Failure to identify the process does not change the TCP result.

---

## 🔐 Safety & Privacy

GhostPort is designed for local diagnostics.

- Connects only to `127.0.0.1` and `::1`.
- Does not offer arbitrary host scanning.
- Never kills, signals, or modifies processes.
- Does not require administrator privileges.
- Does not send telemetry or contact external services.
- Does not follow HTTP redirects.
- Does not read or display HTTP response bodies.
- Disables environment proxy inheritance for HTTP probes.
- Redacts sensitive headers, credentials, query values, and command-line arguments in supported verbose diagnostics.

For vulnerability reporting, see [SECURITY.md](SECURITY.md).

---

## ☁️ Known Limitations

GhostPort is intentionally small and transparent about its capabilities.

- Process identification depends on OS permissions.
- macOS socket inspection may require elevated permissions; GhostPort continues when process information is unavailable.
- Some Windows system processes may expose a PID without a process name.
- Closed loopback ports may take approximately two seconds to report on Windows.
- The default timeout is three seconds and applies per network operation, not as a total execution deadline.
- A JSON content type does not conclusively identify a service.
- TLS-only services are not supported by the plain HTTP probe.
- Only IPv4 and IPv6 loopback addresses are inspected.

---

## 🛠️ Development

```bash
python -m pip install -e ".[dev]"
ruff check .
ruff format --check .
python -m pytest
```

GitHub Actions runs the test and lint checks on Windows, Ubuntu, and macOS using Python 3.11, 3.12, and 3.13.

Want to help improve GhostPort? Read [CONTRIBUTING.md](CONTRIBUTING.md).

---

## ✿ Made in Cyberspace

GhostPort is part of **CyberStudios™**, a creative software ecosystem exploring development tools, game systems, digital environments, and interactive experiences.

Small tools deserve thoughtful engineering, too.

**Developed under CyberStudios™.**

Licensed under the [MIT License](LICENSE).

[Repository](https://github.com/CyberStudiosTM/GhostPort) · [Issues](https://github.com/CyberStudiosTM/GhostPort/issues) · [Security](SECURITY.md)

*End of transmission. The port is still listening.* 👻
