"""Rich terminal rendering (pastel cybercore palette)."""

from __future__ import annotations

from rich import box
from rich.console import Console, Group, RenderableType
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from rich.theme import Theme

from ghostport import __version__
from ghostport.models import HttpResult, InspectionResult, ProcessResult, TcpResult

THEME = Theme(
    {
        "gp.title": "bold #c9b6ff",
        "gp.label": "bold #a9d8ff",
        "gp.ok": "#a8ffd8",
        "gp.warn": "#ffe3a8",
        "gp.bad": "#ff9fc2",
        "gp.dim": "#9aa5c4",
    }
)

_MARK = {"ok": ("[+]", "gp.ok"), "warn": ("[~]", "gp.warn"), "bad": ("[x]", "gp.bad")}


def make_console(**kwargs: object) -> Console:
    return Console(theme=THEME, highlight=False, **kwargs)  # type: ignore[arg-type]


def _line(level: str, *parts: tuple[str, str | None]) -> Text:
    mark, style = _MARK[level]
    text = Text()
    text.append(mark + " ", style=style)
    for value, part_style in parts:
        text.append(value, style=part_style)
    return text


def _tcp_line(tcp: TcpResult) -> Text:
    if tcp.connected:
        return _line("ok", (f"open on {tcp.address}", None), (f"  {tcp.latency_ms} ms", "gp.dim"))
    level = "warn" if tcp.status == "timeout" else "bad"
    return _line(level, (tcp.status, None), (f"  {tcp.error or ''}", "gp.dim"))


def _process_line(proc: ProcessResult) -> Text:
    if proc.status == "identified":
        return _line("ok", (f"{proc.name}", "bold"), (f"  pid {proc.pid}", "gp.dim"))
    if proc.status == "partial":
        return _line(
            "warn", (f"pid {proc.pid}", None), (f"  name unavailable: {proc.reason}", "gp.dim")
        )
    label = "no listener found" if proc.status == "not_found" else "unavailable"
    return _line("warn", (label, None), (f"  {proc.reason}", "gp.dim"))


def _http_line(http: HttpResult) -> Text:
    if http.status == "ok":
        text = _line("ok", (f"{http.status_code}", "bold"))
        text.append(f"  {http.content_type or 'no content-type'}", style=None)
        text.append(f"  {http.response_time_ms} ms", style="gp.dim")
        text.append(f"  server: {http.server or 'not sent'}", style="gp.dim")
        return text
    level = "warn" if http.status in ("timeout", "skipped") else "bad"
    return _line(level, (http.status, None), (f"  {http.error or ''}", "gp.dim"))


def _verdict(result: InspectionResult) -> Text:
    if not result.tcp.connected:
        return Text("Nothing accepted a localhost connection on this port.", style="gp.bad")
    if result.exit_code == 0:
        return Text(
            "Port is accepting connections. These checks do not conclusively identify the service.",
            style="gp.ok",
        )
    return Text(
        "Port is open, but the HTTP check did not pass. This does not identify the service.",
        style="gp.warn",
    )


def render(result: InspectionResult, console: Console, verbose: bool = False) -> None:
    grid = Table.grid(padding=(0, 2))
    grid.add_column(style="gp.label", no_wrap=True)
    grid.add_column()
    grid.add_row("TCP", _tcp_line(result.tcp))
    grid.add_row("PROCESS", _process_line(result.process))
    if result.http is not None:
        grid.add_row("HTTP", _http_line(result.http))
        if result.http.json_check is not None:
            check = result.http.json_check
            level = "ok" if check.matched else ("bad" if check.matched is False else "warn")
            grid.add_row("JSON", _line(level, (check.message, None)))

    body: list[RenderableType] = [grid, Text(), _verdict(result)]
    if verbose:
        body.append(Text())
        body.append(_verbose_table(result))

    title = Text.assemble(
        ("ghostport", "gp.title"),
        (f" v{__version__}", "gp.dim"),
        (f"  localhost:{result.port}", None),
    )
    console.print(
        Panel(
            Group(*body),
            title=title,
            title_align="left",
            box=box.ROUNDED,
            border_style="#c9b6ff",
            padding=(1, 2),
        )
    )


def _verbose_table(result: InspectionResult) -> Table:
    table = Table.grid(padding=(0, 2))
    table.add_column(style="gp.dim", no_wrap=True)
    table.add_column(overflow="fold")
    for listener in result.process.listeners:
        table.add_row("listener", f"pid={listener.pid} name={listener.name}")
        if listener.exe:
            table.add_row("  exe", listener.exe)
        if listener.cmdline:
            table.add_row("  cmdline", " ".join(listener.cmdline))
    if result.http and result.http.url:
        table.add_row("url", result.http.url)
    if result.http:
        for name, value in result.http.headers:
            table.add_row(f"  {name}", value)
    for key, value in (result.diagnostics or {}).items():
        table.add_row(key, str(value))
    return table
