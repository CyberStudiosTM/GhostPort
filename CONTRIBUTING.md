# Contributing

Thanks for helping improve GhostPort. The project is intentionally small; please keep changes focused.

## Setup

Requires Python 3.11+.

```
git clone https://github.com/CyberStudiosTM/GhostPort.git
cd GhostPort
python -m venv .venv
.venv\Scripts\activate        # Linux/macOS: source .venv/bin/activate
pip install -e ".[dev]"
```

## Before opening a pull request

```
ruff check .
ruff format --check .
python -m pytest
```

CI runs the same checks on Windows, Linux, and macOS.

## Guidelines

- Keep the safety model: localhost only, read-only, no process termination, no elevation, no telemetry.
- Keep TCP, process, and HTTP results independent. A failed process lookup must never change the TCP verdict.
- Do not read or display HTTP response bodies.
- Redact sensitive values in any new verbose output.
- Changes to the JSON output must keep `schema_version` 1 additive; breaking changes require a version bump and README update.
- Add tests for new behavior, using mocks or local test servers. Tests must not contact external hosts.
- Open an issue before starting large features.

By contributing, you agree that your contributions are licensed under the MIT License.
