"""Command-line interface for zensical-updates.

`zensical-updates build` writes the generated Updates section into
``docs/<base>/``; run it before ``zensical build``. `clean` removes that output.
`version`/`info` are maintenance helpers.
"""

from __future__ import annotations

from pathlib import Path
from typing import Annotated

import typer
from rich.console import Console

import zensical_updates as lib
from zensical_updates.build import build_site, clean_site
from zensical_updates.config import Config, load_config
from zensical_updates.model import PostError

app = typer.Typer(
    name="zensical-updates",
    help="Generate a dated Updates section for a zensical site.",
    no_args_is_help=True,
    add_completion=False,
)
console = Console()

_RootOption = Annotated[Path, typer.Option(help="Project root holding zensical.toml.")]
_ConfigOption = Annotated[
    Path | None,
    typer.Option(help="Path to zensical.toml (default: the project root)."),
]


def _resolve_config(root: Path, config: Path | None) -> Config:
    path = config or (root / "zensical.toml")
    return load_config(path) if path.exists() else Config()


@app.command()
def build(root: _RootOption = Path(), config: _ConfigOption = None) -> None:
    """Generate the Updates section under the site's docs directory."""
    cfg = _resolve_config(root, config)
    try:
        result = build_site(cfg, root)
    except PostError as exc:
        console.print(f"[red]error:[/red] {exc}")
        raise typer.Exit(1) from exc
    console.print(
        f"Wrote {len(result.written)} files ({len(result.post_urls)} posts) -> {result.out_dir}"
    )


@app.command()
def clean(root: _RootOption = Path(), config: _ConfigOption = None) -> None:
    """Remove the generated Updates output."""
    cfg = _resolve_config(root, config)
    clean_site(cfg, root)
    console.print(f"Removed {root / 'docs' / cfg.base}")


@app.command()
def version() -> None:
    """Print the installed library version."""
    console.print(f"zensical-updates {lib.__version__}")


@app.command()
def info() -> None:
    """Show the version and the public API surface."""
    console.print(f"zensical-updates {lib.__version__}")
    console.print("public API: " + ", ".join(lib.__all__))
