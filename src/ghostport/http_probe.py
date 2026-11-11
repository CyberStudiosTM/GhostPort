"""Bounded HTTP probe: headers only, no redirects, no body download, no proxies."""

from __future__ import annotations

import time

import httpx

from ghostport import __version__
from ghostport.models import HttpResult, JsonCheck
from ghostport.redact import redact_header, redact_url, truncate

_JSON_MEDIA_TYPES = {"application/json", "text/json"}
MAX_HEADERS = 50


def media_type(content_type: str | None) -> str | None:
    if not content_type:
        return None
    return content_type.split(";", 1)[0].strip().lower() or None


def is_json_media_type(mt: str | None) -> bool:
    return bool(mt) and (mt in _JSON_MEDIA_TYPES or mt.endswith("+json"))  # type: ignore[union-attr]


def check_json(content_type: str | None) -> JsonCheck:
    mt = media_type(content_type)
    if mt is None:
        return JsonCheck(
            matched=False,
            media_type=None,
            message="no Content-Type header; cannot confirm a JSON response",
        )
    if is_json_media_type(mt):
        return JsonCheck(
            matched=True,
            media_type=mt,
            message=f"Content-Type '{mt}' is a JSON media type (body was not inspected)",
        )
    return JsonCheck(
        matched=False,
        media_type=mt,
        message=(
            f"Content-Type '{mt}' is not a JSON media type; "
            "this alone does not identify the service"
        ),
    )


def _url_for(address: str, port: int, path: str) -> str:
    host = f"[{address}]" if ":" in address else address
    return f"http://{host}:{port}{path}"


def probe_http(
    address: str,
    port: int,
    timeout: float,
    *,
    path: str = "/",
    expect_json: bool = False,
    verbose: bool = False,
) -> HttpResult:
    """Issue one streamed GET and record response metadata.

    The body is never read: leaving the stream context closes the connection.
    ``trust_env=False`` keeps environment proxies and netrc out of local diagnostics.
    """
    url = _url_for(address, port, path)
    shown_url = redact_url(url)
    started = time.perf_counter()
    try:
        with (
            httpx.Client(
                timeout=httpx.Timeout(timeout),
                follow_redirects=False,
                trust_env=False,
                headers={"User-Agent": f"ghostport/{__version__}", "Accept": "*/*"},
            ) as client,
            client.stream("GET", url) as response,
        ):
            elapsed = round((time.perf_counter() - started) * 1000, 2)
            content_type = response.headers.get("content-type")
            server = response.headers.get("server")
            headers = (
                tuple(
                    (name, redact_header(name, value))
                    for name, value in list(response.headers.items())[:MAX_HEADERS]
                )
                if verbose
                else ()
            )
            return HttpResult(
                status="ok",
                url=shown_url,
                status_code=response.status_code,
                content_type=truncate(content_type) if content_type else None,
                server=truncate(server) if server else None,
                response_time_ms=elapsed,
                json_check=check_json(content_type) if expect_json else None,
                headers=headers,
            )
    except httpx.TimeoutException:
        return _failure("timeout", shown_url, f"no HTTP response within {timeout:g}s", expect_json)
    except httpx.ConnectError:
        return _failure("error", shown_url, "connection failed before HTTP began", expect_json)
    except (httpx.RemoteProtocolError, httpx.ReadError, httpx.WriteError):
        return _failure(
            "error",
            shown_url,
            "port is open but did not return a valid HTTP response "
            "(it may speak another protocol, such as TLS or raw TCP, or reset the connection)",
            expect_json,
        )
    except httpx.HTTPError as exc:
        return _failure(
            "error", shown_url, f"HTTP probe failed ({type(exc).__name__})", expect_json
        )


def _failure(status: str, url: str, message: str, expect_json: bool) -> HttpResult:
    check = (
        JsonCheck(matched=None, media_type=None, message="not evaluated: no HTTP response")
        if expect_json
        else None
    )
    return HttpResult(
        status=status,  # type: ignore[arg-type]
        url=url,
        error=message,
        json_check=check,
    )
