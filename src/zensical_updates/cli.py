"""Maintenance / introspection CLI for zensical-updates.

A thin helper for inspecting the installed library — the importable API in
`zensical_updates` is the actual product. This CLI is the "help
entry point" and is auto-documented in the site via `mkdocs-typer2`. Add
maintenance subcommands (data dumps, self-checks, migrations) here.
"""

from __future__ import annotations

from typing import Annotated

import typer
from rich.console import Console
from rich.table import Table

import zensical_updates as lib

app = typer.Typer(
    name="zensical-updates",
    help="Maintenance helpers for the zensical-updates library.",
    no_args_is_help=True,
    add_completion=False,
)
console = Console()


@app.command()
def version() -> None:
    """Print the installed library version."""
    console.print(f"zensical-updates {lib.__version__}")


@app.command()
def info() -> None:
    """Show package metadata and the public API surface."""
    table = Table(title="zensical-updates")
    table.add_column("Field", style="bold")
    table.add_column("Value")
    table.add_row("version", lib.__version__)
    table.add_row("public API", ", ".join(lib.__all__))
    console.print(table)


@app.command()
def hello(
    name: Annotated[str, typer.Argument(help="Name to greet.")] = "world",
) -> None:
    """Demo command exercising the public API (``greet``)."""
    console.print(lib.greet(name))
