"""Load the ``[project.extra.zensical_updates]`` config from ``zensical.toml``.

zensical ignores the ``[project.extra]`` namespace, so it is a safe home for our
settings. tomllib reads the table; absent keys fall back to the defaults below.
The site's own ``[project] site_url`` is read too, so emitted links can carry the
sub-path a project Pages deploy is served under.
"""

from __future__ import annotations

import tomllib
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any
from urllib.parse import urlparse

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
    site_url: str = ""

    @property
    def url_base(self) -> str:
        """The URL base for emitted links: the site sub-path joined to ``base``.

        A project Pages site is served under ``site_url``'s path (e.g.
        ``/eth-protocol-fellowship/``); a link that omits it 404s. A root-served
        site has no path, so the base is just ``base`` with no extra slash. The
        on-disk output dir is built from ``base`` alone, so it is unaffected.
        """
        prefix = urlparse(self.site_url).path.rstrip("/")
        return f"{prefix}/{self.base}".strip("/")


def _project(path: Path) -> dict[str, Any]:
    data = tomllib.loads(path.read_text(encoding="utf-8"))
    project = data.get("project") if isinstance(data, dict) else None
    return project if isinstance(project, dict) else {}


def _table(project: dict[str, Any]) -> dict[str, Any]:
    node: Any = project
    for key in ("extra", "zensical_updates"):
        node = node.get(key, {}) if isinstance(node, dict) else {}
    return node if isinstance(node, dict) else {}


def load_config(path: Path) -> Config:
    """Read the config table from ``zensical.toml``, defaulting any absent key."""
    project = _project(path)
    table = _table(project)
    d = Config()
    return Config(
        base=str(table.get("base", d.base)),
        source=str(table.get("source", d.source)),
        intro=str(table.get("intro", d.intro)),
        excerpt_marker=str(table.get("excerpt_marker", d.excerpt_marker)),
        emit_tags=bool(table.get("emit_tags", d.emit_tags)),
        emit_categories=bool(table.get("emit_categories", d.emit_categories)),
        emit_archive=bool(table.get("emit_archive", d.emit_archive)),
        site_url=str(project.get("site_url", d.site_url)),
    )
