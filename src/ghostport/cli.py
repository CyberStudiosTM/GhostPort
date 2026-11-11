"""Typer command-line interface."""

from __future__ import annotations

import json
import sys
from typing import Annotated, NoReturn

import typer

from ghostport import __version__
from ghostport.inspector import inspect_port
from ghostport.models import EXIT_USAGE, error_envelope
from ghostport.render import make_console, render

MIN_TIMEOUT = 0.05
MAX_TIMEOUT = 30.0

app = typer.Typer(
    name="ghostport",
    help="A tiny forensic tool for local TCP ports. Localhost only, read-only, no telemetry.",
    no_args_is_help=True,
    add_completion=False,
)


def _version(value: bool) -> None:
    if value:
        typer.echo(f"ghostport {__version__}")
        raise typer.Exit()


@app.callback()
def _root(
    version: Annotated[
        bool,
        typer.Option("--version", callback=_version, is_eager=True, help="Show version and exit."),
    ] = False,
) -> None:
    """GhostPort."""


def _fail(code: str, message: str, as_json: bool) -> NoReturn:
    if as_json:
        typer.echo(json.dumps(error_envelope(code, message), indent=2))
    else:
        make_console(stderr=True).print(
            f"[gp.bad]error:[/] {message}", markup=True, highlight=False
        )
    raise typer.Exit(EXIT_USAGE)


def _parse_port(raw: str, as_json: bool) -> int:
    try:
        port = int(raw.strip(), 10)
    except ValueError:
        _fail("invalid_port", f"invalid port {raw!r}: expected an integer from 1 to 65535", as_json)
    if not 1 <= port <= 65535:
        _fail("invalid_port", f"invalid port {port}: must be between 1 and 65535", as_json)
    return port


@app.command("inspect")
def inspect_command(
    port: Annotated[str, typer.Argument(metavar="PORT", help="TCP port on localhost (1-65535).")],
    http: Annotated[bool, typer.Option("--http", help="Send one bounded HTTP GET.")] = False,
    expect_json: Annotated[
        bool, typer.Option("--expect-json", help="Check that Content-Type is a JSON media type.")
    ] = False,
    json_output: Annotated[
        bool, typer.Option("--json", help="Emit stable machine-readable JSON.")
    ] = False,
    verbose: Annotated[
        bool, typer.Option("--verbose", "-v", help="Add diagnostics (sensitive values redacted).")
    ] = False,
    timeout: Annotated[
        float, typer.Option("--timeout", "-t", help="Per-operation timeout in seconds.")
    ] = 3.0,
    path: Annotated[str, typer.Option("--path", help="Request path for --http.")] = "/",
) -> None:
    """Inspect a localhost TCP port: connectivity, owning process, optional HTTP probe."""
    number = _parse_port(port, json_output)
    if not MIN_TIMEOUT <= timeout <= MAX_TIMEOUT:
        _fail(
            "invalid_timeout",
            f"timeout must be between {MIN_TIMEOUT:g} and {MAX_TIMEOUT:g} seconds",
            json_output,
        )
    if expect_json and not http:
        _fail("usage", "--expect-json requires --http", json_output)
    if not path.startswith("/") or any(c in path for c in " \r\n\t"):
        _fail("invalid_path", "--path must start with '/' and contain no whitespace", json_output)

    result = inspect_port(
        number, timeout=timeout, http=http, expect_json=expect_json, path=path, verbose=verbose
    )
    if json_output:
        typer.echo(json.dumps(result.to_dict(verbose), indent=2))
    else:
        render(result, make_console(), verbose)
    raise typer.Exit(result.exit_code)


def main() -> None:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(errors="replace")
    app()


if __name__ == "__main__":
    main()
