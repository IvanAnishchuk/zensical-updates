"""Load the ``[project.extra.zensical_updates]`` config from ``zensical.toml``.

zensical ignores the ``[project.extra]`` namespace, so it is a safe home for our
settings. tomllib reads the table; absent keys fall back to the defaults below.
"""

from __future__ import annotations

import tomllib
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from pathlib import Path


@dataclass(frozen=True)
class Config:
    """Resolved generator settings."""

    base: str = "updates"
    source: str = "updates"
    intro: str = "index.md"
    excerpt_marker: str = "<!-- more -->"
    emit_tags: bool = True
    emit_categories: bool = True
    emit_archive: bool = True


def _table(path: Path) -> dict[str, Any]:
    data = tomllib.loads(path.read_text(encoding="utf-8"))
    node: Any = data
    for key in ("project", "extra", "zensical_updates"):
        node = node.get(key, {}) if isinstance(node, dict) else {}
    return node if isinstance(node, dict) else {}


def load_config(path: Path) -> Config:
    """Read the config table from ``zensical.toml``, defaulting any absent key."""
    table = _table(path)
    d = Config()
    return Config(
        base=str(table.get("base", d.base)),
        source=str(table.get("source", d.source)),
        intro=str(table.get("intro", d.intro)),
        excerpt_marker=str(table.get("excerpt_marker", d.excerpt_marker)),
        emit_tags=bool(table.get("emit_tags", d.emit_tags)),
        emit_categories=bool(table.get("emit_categories", d.emit_categories)),
        emit_archive=bool(table.get("emit_archive", d.emit_archive)),
    )
