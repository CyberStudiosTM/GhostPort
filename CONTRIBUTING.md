# 🌱 Contributing to GhostPort

**Welcome to the little corner of cyberspace where GhostPort lives.**

GhostPort is a CyberStudios™ open-source project built around a simple idea: developer tools can be lightweight, reliable, and pleasant to use.

Whether you're fixing a bug, improving documentation, adding a regression test, or investigating a platform-specific issue, contributions are welcome.

## ✦ Before You Begin

GhostPort is intentionally focused.

Its purpose is to inspect local TCP ports and report observable diagnostic information. Contributions should preserve that purpose rather than expand the project into a general-purpose network scanner.

For larger features, please open an issue to discuss the proposed scope before implementation.

## 🖥️ Development Setup

Requires Python 3.11 or newer.

Clone the repository:

```bash
git clone https://github.com/CyberStudiosTM/GhostPort.git
cd GhostPort
```

Create a virtual environment:

```bash
python -m venv .venv
```

Activate it on Windows PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

Or on Linux/macOS:

```bash
source .venv/bin/activate
```

Install development dependencies:

```bash
python -m pip install -e ".[dev]"
```

## 🧪 Test Before You Submit

Run the project's checks:

```bash
ruff check .
ruff format --check .
python -m pytest
```

The GitHub Actions workflow also tests Windows, Ubuntu, and macOS across supported Python versions.

If a check cannot run in your environment, explain that limitation in your pull request.

## 🌿 Contribution Guidelines

### Keep it local

GhostPort only inspects IPv4 and IPv6 loopback addresses. Do not introduce arbitrary remote scanning, telemetry, or background monitoring.

### Preserve read-only behavior

GhostPort must not terminate, signal, or modify processes.

### Keep diagnostics independent

TCP connectivity, process identification, and HTTP checks are separate observations.

A process lookup failure must not turn a successful TCP result into a failure.

### Respect response boundaries

HTTP inspection must not read or display response bodies.

Keep requests bounded, avoid following redirects, and preserve the existing proxy isolation.

### Protect sensitive information

New diagnostic output must not expose credentials, authentication headers, tokens, or other sensitive values.

### Maintain the JSON contract

Additive changes may retain `schema_version: 1`. Breaking changes require a schema-version update and corresponding documentation.

### Test the behavior

Add or update regression tests when changing functionality.

Tests should use mocks or local test servers and must not depend on external hosts.

## ✿ Opening a Pull Request

A useful pull request should explain:

1. What changed and why.
2. Which issue or behavior it addresses.
3. What tests were run.
4. Any platform-specific limitations.
5. Whether the JSON schema, CLI behavior, or documented safety boundaries changed.

Keep pull requests focused and reviewable.

## ♡ Code of Conduct

Be respectful, constructive, and considerate when discussing issues or reviewing contributions.

Disagreements about implementation are normal. Personal attacks, harassment, and discriminatory behavior are not welcome.

This section describes project expectations and does not imply a separate formal Code of Conduct policy exists.

## 📜 Licensing

By contributing, you agree that your contributions are licensed under the project's [MIT License](LICENSE).

---

**Thanks for helping GhostPort grow.**

*Every good tool starts somewhere. Sometimes that somewhere is localhost.* 👻

**CyberStudios™**
