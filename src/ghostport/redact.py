"""Redaction helpers so verbose output never leaks credentials."""

from __future__ import annotations

import re
from collections.abc import Iterable
from pathlib import Path

REDACTED = "***"

_SENSITIVE_NAME = re.compile(
    r"auth|token|secret|passw|pwd|key|cookie|session|credential|bearer|signature|sig$",
    re.IGNORECASE,
)
_QUERY_PAIR = re.compile(r"([?&;])([^=&;\s]+)=([^&;\s]*)")
_USERINFO = re.compile(r"(://)[^/@\s]+@")

MAX_VALUE_LEN = 200
MAX_ARGS = 20


def is_sensitive_name(name: str) -> bool:
    return bool(_SENSITIVE_NAME.search(name))


def truncate(value: str, limit: int = MAX_VALUE_LEN) -> str:
    return value if len(value) <= limit else value[: limit - 3] + "..."


def redact_text(value: str) -> str:
    """Mask URL credentials and sensitive query values inside free text."""

    def _query(match: re.Match[str]) -> str:
        sep, key, val = match.groups()
        return f"{sep}{key}={REDACTED if is_sensitive_name(key) else val}"

    return _QUERY_PAIR.sub(_query, _USERINFO.sub(r"\1" + REDACTED + "@", value))


def redact_header(name: str, value: str) -> str:
    if is_sensitive_name(name):
        return REDACTED
    return truncate(redact_text(value))


def redact_url(url: str) -> str:
    return redact_text(url)


def redact_path(path: str) -> str:
    home = str(Path.home())
    if home and path.lower().startswith(home.lower()):
        return "~" + path[len(home) :]
    return path


def redact_cmdline(args: Iterable[str]) -> tuple[str, ...]:
    """Mask values of sensitive flags (`--token=x`, `--token x`, `KEY=x`) and URL userinfo."""
    out: list[str] = []
    mask_next = False
    for raw in args:
        if len(out) >= MAX_ARGS:
            out.append("...")
            break
        if mask_next:
            out.append(REDACTED)
            mask_next = False
            continue
        if "=" in raw:
            key, _, _val = raw.partition("=")
            if is_sensitive_name(key):
                out.append(f"{key}={REDACTED}")
                continue
        elif raw.startswith("-") and is_sensitive_name(raw):
            out.append(raw)
            mask_next = True
            continue
        out.append(truncate(redact_text(raw)))
    return tuple(out)
