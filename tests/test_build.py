"""Tests for the build orchestration."""

from dataclasses import replace
from pathlib import Path

import feedparser
import pytest

from zensical_updates import load_config
from zensical_updates.build import build_site, clean_site
from zensical_updates.config import Config


def _write_post(
    dir_path: Path,
    slug: str,
    date: str,
    *,
    categories: tuple[str, ...] = (),
    tags: tuple[str, ...] = (),
) -> None:
    text = f"---\ndate: {date}\n"
    if categories:
        text += "categories:\n" + "".join(f"  - {c}\n" for c in categories)
    if tags:
        text += "tags:\n" + "".join(f"  - {t}\n" for t in tags)
    text += f"---\n\nBody of {slug}.\n"
    (dir_path / f"{slug}.md").write_text(text, encoding="utf-8")


def test_build_copies_posts_and_writes_pages(tmp_path: Path) -> None:
    src = tmp_path / "updates"
    src.mkdir()
    (src / "index.md").write_text("# Updates\n\nWelcome.\n", encoding="utf-8")
    _write_post(src, "hello", "2026-06-11", categories=("weekly-update",), tags=("epf",))

    result = build_site(Config(), tmp_path)
    out = tmp_path / "docs" / "updates"

    assert (out / "hello.md").exists()  # post copied verbatim
    index = (out / "index.md").read_text(encoding="utf-8")
    assert "Welcome." in index  # intro carried through
    assert "[hello](/updates/hello/)" in index  # listing links the post
    assert (out / "archive" / "2026" / "index.md").exists()
    assert (out / "tags" / "epf" / "index.md").exists()
    assert (out / "categories" / "weekly-update" / "index.md").exists()
    assert "/updates/hello/" in result.post_urls


def test_build_links_carry_the_site_subpath(tmp_path: Path) -> None:
    src = tmp_path / "updates"
    src.mkdir()
    (src / "index.md").write_text("# Updates\n\nWelcome.\n", encoding="utf-8")
    _write_post(src, "hello", "2026-06-11", categories=("weekly-update",), tags=("epf",))

    cfg = Config(site_url="https://example.github.io/repo/", emit_feed=False)
    result = build_site(cfg, tmp_path)
    out = tmp_path / "docs" / "updates"

    index = (out / "index.md").read_text(encoding="utf-8")
    assert "[hello](/repo/updates/hello/)" in index  # post link carries the base path
    assert "/repo/updates/tags/epf/" in index  # taxonomy link too
    assert "/repo/updates/hello/" in result.post_urls
    assert (out / "hello.md").exists()  # on-disk output dir is unchanged by the base path


def test_build_links_have_no_double_slash_when_root_served(tmp_path: Path) -> None:
    src = tmp_path / "updates"
    src.mkdir()
    (src / "index.md").write_text("# Updates\n\nWelcome.\n", encoding="utf-8")
    _write_post(src, "hello", "2026-06-11", tags=("epf",))

    # No site_url (root-served site): links stay /updates/... with no extra slash.
    result = build_site(Config(), tmp_path)
    index = (tmp_path / "docs" / "updates" / "index.md").read_text(encoding="utf-8")
    assert "[hello](/updates/hello/)" in index
    assert "//" not in index
    assert result.post_urls == ["/updates/hello/"]


def test_build_does_not_mutate_the_source(tmp_path: Path) -> None:
    src = tmp_path / "updates"
    src.mkdir()
    _write_post(src, "hello", "2026-06-11")
    before = (src / "hello.md").read_text(encoding="utf-8")
    build_site(Config(), tmp_path)
    assert (src / "hello.md").read_text(encoding="utf-8") == before


def test_clean_removes_the_output_tree(tmp_path: Path) -> None:
    out = tmp_path / "docs" / "updates"
    out.mkdir(parents=True)
    (out / "index.md").write_text("x", encoding="utf-8")
    clean_site(Config(), tmp_path)
    assert not out.exists()


def test_build_can_disable_taxonomies_and_archive(tmp_path: Path) -> None:
    src = tmp_path / "updates"
    src.mkdir()
    _write_post(src, "hello", "2026-06-11", categories=("news",), tags=("epf",))
    cfg = Config(emit_archive=False, emit_tags=False, emit_categories=False)
    build_site(cfg, tmp_path)
    out = tmp_path / "docs" / "updates"
    assert (out / "index.md").exists()
    assert not (out / "archive").exists()
    assert not (out / "tags").exists()
    assert not (out / "categories").exists()


def _write_site(tmp_path: Path, *, site_url: str) -> None:
    toml = '[project]\nsite_name = "S"\n'
    if site_url:
        toml += f'site_url = "{site_url}"\n'
    toml += 'docs_dir = "docs"\nsite_dir = "site"\n'
    (tmp_path / "zensical.toml").write_text(toml, encoding="utf-8")
    src = tmp_path / "updates"
    src.mkdir()
    (src / "index.md").write_text("# Updates\n\nIntro.\n", encoding="utf-8")
    for i, day in enumerate(("2026-06-11", "2026-05-01", "2026-04-01")):
        (src / f"p{i}.md").write_text(f"---\ndate: {day}\n---\n\nBody {i}.\n", encoding="utf-8")


def test_build_skips_feed_without_site_url(tmp_path: Path) -> None:
    _write_site(tmp_path, site_url="")
    cfg = load_config(tmp_path / "zensical.toml")
    result = build_site(cfg, tmp_path)
    assert result.feed_path is None
    assert not (tmp_path / "docs" / "updates" / "feed.xml").exists()


def test_build_writes_feed_when_site_url_set(tmp_path: Path) -> None:
    pytest.importorskip("zensical")
    _write_site(tmp_path, site_url="https://example.github.io/repo/")
    cfg = load_config(tmp_path / "zensical.toml")
    result = build_site(cfg, tmp_path)
    assert result.feed_path is not None
    assert result.feed_path == tmp_path / "docs" / "updates" / "feed.xml"
    assert result.feed_path.exists()


def test_build_main_index_has_browse_nav(tmp_path: Path) -> None:
    src = tmp_path / "updates"
    src.mkdir()
    (src / "index.md").write_text("# Updates\n\nWelcome.\n", encoding="utf-8")
    _write_post(src, "hello", "2026-06-11", categories=("weekly-update",), tags=("epf",))
    build_site(Config(), tmp_path)
    index = (tmp_path / "docs" / "updates" / "index.md").read_text(encoding="utf-8")
    assert "Browse: [Tags](/updates/tags/)" in index


def test_build_browse_nav_drops_disabled_indexes(tmp_path: Path) -> None:
    src = tmp_path / "updates"
    src.mkdir()
    _write_post(src, "hello", "2026-06-11", tags=("epf",))
    build_site(Config(emit_categories=False), tmp_path)
    index = (tmp_path / "docs" / "updates" / "index.md").read_text(encoding="utf-8")
    assert "[Tags](/updates/tags/)" in index
    assert "[Categories]" not in index


def test_build_respects_feed_limit(tmp_path: Path) -> None:
    pytest.importorskip("zensical")
    _write_site(tmp_path, site_url="https://example.github.io/repo/")
    limit = 2
    cfg = replace(load_config(tmp_path / "zensical.toml"), feed_limit=limit)
    build_site(cfg, tmp_path)
    parsed = feedparser.parse((tmp_path / "docs" / "updates" / "feed.xml").read_text("utf-8"))
    assert len(parsed.entries) == limit
