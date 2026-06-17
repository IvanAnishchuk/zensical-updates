"""Integration test: generate, build with ``zensical --strict``, verify links.

This is the decisive test. It guards the two silent failures: a generated post
link that does not match zensical's rendered path, and front matter or markup the
strict link validator rejects. Both ship green without this end-to-end check,
because zensical does not validate site-absolute links.
"""

from __future__ import annotations

import subprocess
import sys
from typing import TYPE_CHECKING

import pytest

from zensical_updates import Config, build_site, load_config

if TYPE_CHECKING:
    from pathlib import Path

pytest.importorskip("zensical")

_ZENSICAL_TOML = """\
[project]
site_name = "Fixture"
docs_dir = "docs"
site_dir = "site"

nav = [
    { "Updates" = "updates/index.md" },
]
"""

_ZENSICAL_TOML_SUBPATH = """\
[project]
site_name = "Fixture"
site_url = "https://example.github.io/repo/"
docs_dir = "docs"
site_dir = "site"

nav = [
    { "Updates" = "updates/index.md" },
]
"""


def _post(date: str, *, categories: tuple[str, ...] = (), tags: tuple[str, ...] = ()) -> str:
    text = f"---\ndate: {date}\n"
    if categories:
        text += "categories:\n" + "".join(f"  - {c}\n" for c in categories)
    if tags:
        text += "tags:\n" + "".join(f"  - {t}\n" for t in tags)
    return text + "---\n\nSome body text for the post.\n"


def test_generated_links_resolve_under_strict_build(tmp_path: Path) -> None:
    root = tmp_path
    (root / "zensical.toml").write_text(_ZENSICAL_TOML, encoding="utf-8")
    src = root / "updates"
    src.mkdir()
    (src / "index.md").write_text("# Updates\n\nWelcome to the updates.\n", encoding="utf-8")
    (src / "hello.md").write_text(
        _post("2026-06-11", categories=("weekly-update",), tags=("epf",)), encoding="utf-8"
    )
    (src / "world.md").write_text(
        _post("2026-05-01", categories=("news",), tags=("epf",)), encoding="utf-8"
    )

    result = build_site(Config(), root)

    proc = subprocess.run(
        [sys.executable, "-m", "zensical", "build", "--clean", "--strict"],
        cwd=root,
        capture_output=True,
        text=True,
        check=False,
    )
    assert proc.returncode == 0, f"zensical --strict failed:\n{proc.stdout}\n{proc.stderr}"

    site = root / "site"
    for url in result.post_urls:
        rel = url.strip("/")  # e.g. "updates/hello"
        assert (site / rel / "index.html").exists(), f"no rendered page for {url}"
    assert (site / "updates" / "index.html").exists()
    assert (site / "updates" / "archive" / "2026" / "index.html").exists()
    assert (site / "updates" / "tags" / "epf" / "index.html").exists()
    assert (site / "updates" / "categories" / "weekly-update" / "index.html").exists()


def test_generated_links_resolve_on_a_subpath_site(tmp_path: Path) -> None:
    # The bug: a project Pages site served under /repo/ got links that omitted
    # /repo and 404'd. Emitted links must carry the base path; the built files
    # stay unprefixed (the prefix is the serve path, not the on-disk path).
    root = tmp_path
    (root / "zensical.toml").write_text(_ZENSICAL_TOML_SUBPATH, encoding="utf-8")
    src = root / "updates"
    src.mkdir()
    (src / "index.md").write_text("# Updates\n\nWelcome to the updates.\n", encoding="utf-8")
    (src / "hello.md").write_text(
        _post("2026-06-11", categories=("weekly-update",), tags=("epf",)), encoding="utf-8"
    )

    cfg = load_config(root / "zensical.toml")
    result = build_site(cfg, root)

    proc = subprocess.run(
        [sys.executable, "-m", "zensical", "build", "--clean", "--strict"],
        cwd=root,
        capture_output=True,
        text=True,
        check=False,
    )
    assert proc.returncode == 0, f"zensical --strict failed:\n{proc.stdout}\n{proc.stderr}"

    site = root / "site"
    prefix = "/repo"
    for url in result.post_urls:
        assert url.startswith(prefix + "/"), f"link {url} omits the {prefix} base path"
        rel = url[len(prefix) :].strip("/")  # strip the serve prefix to find the file
        assert (site / rel / "index.html").exists(), f"no rendered page for {url}"
    assert (site / "updates" / "tags" / "epf" / "index.html").exists()
