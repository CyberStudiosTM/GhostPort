# Security Policy

## Scope

GhostPort is a read-only, localhost-only diagnostic tool. It contacts only `127.0.0.1` and `::1`, never modifies or terminates processes, and sends no telemetry.

Reports of interest include:

- Any way to make GhostPort contact a non-loopback host.
- Leaks of sensitive values (headers, URL credentials, command-line arguments) in `--verbose` or `--json` output.
- Crashes or hangs caused by hostile local services (for example oversized or malformed responses).

## Reporting a vulnerability

Please report privately through GitHub: open the repository's **Security** tab and choose **Report a vulnerability**. Do not open a public issue for security problems.

Include the GhostPort version (`ghostport --version`), your OS, and steps to reproduce. We aim to acknowledge reports within 7 days.

## Supported versions

Only the latest released version receives security fixes.
